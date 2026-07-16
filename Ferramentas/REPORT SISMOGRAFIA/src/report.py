from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import fitz
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


PAGE_W, PAGE_H = A4
FIRST_PAGE_CARD_SLOTS = 3
# A primeira página fica dedicada ao resumo e aos pontos; os gráficos ganham
# uma página própria para não serem reduzidos a miniaturas ilegíveis.
FIRST_PAGE_LAST_CARD_Y = 220
POINT_CARD_HEIGHT = 58
POINT_CARD_GAP = 14
POINTS_TITLE_GAP = 22
CHART_TO_POINTS_GAP = 40
CHARTS_TOP_LIMIT = 480
COLORS = {
    "red": "#E30613",
    "green": "#67C70A",
    "dark": "#3C4656",
    "navy": "#151B36",
    "text": "#111827",
    "muted": "#667085",
    "line": "#D9DEE7",
    "light_green": "#EAF6D9",
    "shadow": "#E1E5EA",
}


def fmt_num(value, digits=3, comma=True):
    if value is None:
        return "N/D"
    txt = f"{float(value):.{digits}f}"
    if comma:
        txt = txt.replace('.', ',')
    return txt


def fmt_date_iso(value: str | None) -> str:
    if not value:
        return "N/D"
    parts = str(value).split('-')
    if len(parts) == 3:
        return f"{parts[2]}/{parts[1]}/{parts[0]}"
    return str(value)


def _hex(c: canvas.Canvas, value: str):
    c.setFillColor(value)
    c.setStrokeColor(value)


def _draw_round_rect(c: canvas.Canvas, x: float, y: float, w: float, h: float, radius: float = 5, fill: str = "#FFFFFF", stroke: str | None = None, shadow: bool = True):
    if shadow:
        c.setFillColor(COLORS["shadow"])
        c.roundRect(x + 2, y - 2, w, h, radius, stroke=0, fill=1)
    c.setFillColor(fill)
    c.setStrokeColor(stroke or fill)
    c.roundRect(x, y, w, h, radius, stroke=1 if stroke else 0, fill=1)


def _section_header(c: canvas.Canvas, x: float, y: float, w: float, h: float, title: str, color: str = COLORS["green"]):
    c.setFillColor(color)
    c.roundRect(x, y, w, h, 5, stroke=0, fill=1)
    c.setFillColor("white")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x + 12, y + h - 13, title)


def _draw_text(c: canvas.Canvas, text: str, x: float, y: float, size: float = 8, color: str = COLORS["text"], bold: bool = False):
    c.setFillColor(color)
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    c.drawString(x, y, str(text))


def _fit_image(c: canvas.Canvas, image_path: str | Path, x: float, y: float, w: float, h: float):
    image_path = Path(image_path)
    if not image_path.exists():
        return
    img = ImageReader(str(image_path))
    iw, ih = img.getSize()
    scale = min(w / iw, h / ih)
    nw, nh = iw * scale, ih * scale
    c.drawImage(img, x + (w - nw) / 2, y + (h - nh) / 2, width=nw, height=nh, mask='auto')


def _draw_header(c: canvas.Canvas, config: Dict, records: List[Dict], summary: Dict):
    margin = 28
    logo = Path(config.get("branding", {}).get("logo_path", "assets/enaex_logo.png"))
    if not logo.is_absolute():
        logo = Path(__file__).resolve().parents[1] / logo
    _fit_image(c, logo, margin, PAGE_H - 62, 112, 30)

    # Selo geométrico discreto: círculo com o número de pontos.
    c.setStrokeColor(COLORS["dark"])
    c.setLineWidth(1)
    c.circle(PAGE_W - 52, PAGE_H - 46, 14, stroke=1, fill=0)
    _draw_text(c, str(len(records)), PAGE_W - 55, PAGE_H - 50, 12, COLORS["dark"], bold=True)

    x, y, w, h = margin, PAGE_H - 144, PAGE_W - 2 * margin, 78
    _draw_round_rect(c, x, y, w, h, radius=5, fill="#FFFFFF", shadow=True)
    # Faixa superior discreta em cinza claro (troca do cinza médio anterior, menos pesado).
    c.setFillColor("#E8EAEE")
    c.roundRect(x, y + h - 10, w, 10, 5, stroke=0, fill=1)

    _draw_text(c, config.get("project", {}).get("title", "MONITORAMENTO SISMOGRÁFICO"), x + 22, y + 46, 15, COLORS["red"], bold=True)
    client = summary.get("client") or config.get("project", {}).get("client_default", "US MINERAÇÃO VALE-VERDE")
    _draw_text(c, str(client).upper(), x + 22, y + 26, 11, "#697386", bold=True)
    _draw_text(c, f"{len(records)} ponto(s)", x + 22, y + 12, 8, COLORS["text"], bold=True)


def _draw_scope(c: canvas.Canvas, x: float, y: float, w: float, h: float, config: Dict, records: List[Dict], summary: Dict):
    _draw_round_rect(c, x, y, w, h, radius=5, fill="#FFFFFF", shadow=True)
    _section_header(c, x, y + h - 20, w, 20, "Escopo da Campanha")
    y0 = y + h - 32
    event_date = fmt_date_iso(summary.get("event_date"))
    client = summary.get("client") or config.get("project", {}).get("client_default", "N/D")
    _draw_text(c, f"Data do evento: {event_date}", x + 12, y0, 8)
    _draw_text(c, f"Cliente: {client}", x + 12, y0 - 11, 8)
    _draw_text(c, f"Pontos monitorados: {len(records)} fonte(s) de dados de sismógrafos processadas com sucesso.", x + 12, y0 - 22, 8)
    if config.get("report", {}).get("show_vibration_index", True):
        vib_limit = config.get("limits", {}).get("vibration_status_mm_s", 0.8)
        status = "abaixo" if summary.get("all_below_configured_vibration_limit") else "acima"
        _draw_text(c, f"■ Índices de vibração: {status} de {str(vib_limit).replace('.', ',')} mm/s.", x + 12, y0 - 33, 8, COLORS["green"], bold=True)


def _draw_conclusion(c: canvas.Canvas, x: float, y: float, w: float, h: float, records: List[Dict], summary: Dict):
    _draw_round_rect(c, x, y, w, h, radius=5, fill="#FFFFFF", shadow=True)
    _section_header(c, x, y + h - 20, w, 20, "Conclusão Técnica")

    rows = [
        ("Conformidade", "Todos os pontos abaixo dos limites da ABNT NBR 9653:2018." if summary.get("all_conforme_abnt") else "Há ponto(s) acima de limite ou com dado ausente para avaliação."),
        ("Maior PSPL", f"{fmt_num(summary.get('max_pspl', {}).get('value_db'), 1)} dB(L) | {summary.get('max_pspl', {}).get('point_name') or 'N/D'}"),
        ("Maior PPV", f"{fmt_num(summary.get('max_ppv', {}).get('value_mm_s'), 3)} mm/s | {summary.get('max_ppv', {}).get('point_name') or 'N/D'}"),
        ("Maior PVS", f"{fmt_num(summary.get('max_pvs', {}).get('value_mm_s'), 3)} mm/s | {summary.get('max_pvs', {}).get('point_name') or 'N/D'}"),
    ]
    table_x, table_y = x + 12, y + 8
    row_h = 11
    col1 = 88
    total_w = w - 24
    for i, (label, value) in enumerate(rows):
        yy = table_y + (len(rows) - 1 - i) * row_h
        # Faixa de rótulo em verde-claro (sem bordas); linha separadora sutil abaixo.
        c.setFillColor(COLORS["light_green"])
        c.rect(table_x, yy, col1, row_h, fill=1, stroke=0)
        if i < len(rows) - 1:
            c.setStrokeColor(COLORS["line"])
            c.setLineWidth(0.4)
            c.line(table_x + col1, yy, table_x + total_w, yy)
        _draw_text(c, label, table_x + 6, yy + 3, 7, COLORS["text"], bold=True)
        _draw_text(c, value, table_x + col1 + 6, yy + 3, 7, COLORS["text"])


def _draw_chart_card(c: canvas.Canvas, x: float, y: float, w: float, h: float, title: str, image_path: str):
    _draw_round_rect(c, x, y, w, h, radius=5, fill="#FFFFFF", shadow=True)
    _section_header(c, x, y + h - 20, w, 20, title)
    _fit_image(c, image_path, x + 9, y + 10, w - 18, h - 38)


def _draw_chart_page(c: canvas.Canvas, config: Dict, charts: Dict[str, str]):
    margin = 28
    chart_cfg = config.get("charts", {})
    card_h = float(chart_cfg.get("report_chart_page_card_height", 300))
    gap = float(chart_cfg.get("report_chart_page_gap", 24))
    title = chart_cfg.get("report_chart_page_title", "Gráficos Normativos — ABNT NBR 9653:2018")
    chart_w = PAGE_W - 2 * margin
    top_y = PAGE_H - 86 - card_h
    bottom_y = top_y - gap - card_h

    _draw_text(c, title, margin, PAGE_H - 55, 17, COLORS["text"])
    c.setFillColor(COLORS["green"])
    c.rect(margin, PAGE_H - 62, 42, 2, stroke=0, fill=1)
    _draw_chart_card(c, margin, top_y, chart_w, card_h, "Pressão Sonora x Distância", charts["pressure_chart"])
    _draw_chart_card(c, margin, bottom_y, chart_w, card_h, "PPV x Limite ABNT", charts["vibration_chart"])
    _draw_footer(c, config)


def _point_status_text(record: Dict) -> Tuple[str, str]:
    ok = record.get("evaluation", {}).get("overall_conforme_abnt")
    if ok is True:
        return "CONFORME ABNT", COLORS["green"]
    if ok is False:
        return "VERIFICAR", COLORS["red"]
    return "DADO AUSENTE", "#9AA1AC"


def _draw_point_card(c: canvas.Canvas, x: float, y: float, w: float, h: float, record: Dict):
    _draw_round_rect(c, x, y, w, h, radius=5, fill="#FFFFFF", shadow=True)
    c.setFillColor(COLORS["dark"])
    c.roundRect(x, y + h - 17, w, 17, 4, stroke=0, fill=1)
    # Régua verde à esquerda do cabeçalho — conecta com a paleta das seções.
    c.setFillColor(COLORS["green"])
    c.rect(x, y + h - 17, 3.5, 17, stroke=0, fill=1)
    _draw_text(c, str(record.get("point_name", "PONTO MONITORADO")).upper(), x + 14, y + h - 12, 9, "white", bold=True)

    table_x = x + 12
    table_y = y + 7
    row_h = 11
    label_w = 42
    col_pairs = [
        [("Data", fmt_date_iso(record.get("event_date"))), ("PSPL", f"{fmt_num(record.get('pspl_db'), 1)} dB(L)"), ("Mic", f"{fmt_num(record.get('mic_freq_hz'), 1)} Hz")],
        [("PVS", f"{fmt_num(record.get('pvs_mm_s'), 3)} mm/s"), ("SD", fmt_num(record.get('scaled_distance'), 1)), ("Dist / Carga", f"{fmt_num(record.get('gps_distance_m'), 1)} m | {fmt_num(record.get('charge_kg'), 1)} kg")],
        [("Tran", f"{fmt_num(record.get('tran_ppv_mm_s'), 3)} mm/s | {fmt_num(record.get('tran_freq_hz'), 1)} Hz"), ("Vert", f"{fmt_num(record.get('vert_ppv_mm_s'), 3)} mm/s | {fmt_num(record.get('vert_freq_hz'), 1)} Hz"), ("Long", f"{fmt_num(record.get('long_ppv_mm_s'), 3)} mm/s | {fmt_num(record.get('long_freq_hz'), 1)} Hz")],
    ]
    # Renderiza em três blocos horizontais, cada bloco com 3 linhas.
    block_w = 135
    for block_idx, rows in enumerate(col_pairs):
        bx = table_x + block_idx * (block_w + 5)
        for i, (label, value) in enumerate(rows):
            yy = table_y + (2 - i) * row_h
            c.setFillColor(COLORS["light_green"])
            c.rect(bx, yy, label_w, row_h, fill=1, stroke=0)
            if i < 2:
                c.setStrokeColor(COLORS["line"])
                c.setLineWidth(0.35)
                c.line(bx + label_w, yy, bx + block_w, yy)
            _draw_text(c, label, bx + 5, yy + 3, 5.8, COLORS["text"], bold=True)
            _draw_text(c, value, bx + label_w + 5, yy + 3, 5.8, COLORS["text"])

    label, color = _point_status_text(record)
    btn_w, btn_h = 96, 18
    c.setFillColor(color)
    c.roundRect(x + w - btn_w - 12, y + 13, btn_w, btn_h, 9, stroke=0, fill=1)
    _draw_text(c, label, x + w - btn_w + 6, y + 19, 7.5, "white", bold=True)


def _draw_footer(c: canvas.Canvas, config: Dict):
    badge_w, badge_h = 112, 22
    badge_x, badge_y = PAGE_W - 145, 16
    # Texto normativo alinhado verticalmente ao centro do badge.
    _draw_text(c, f"Base normativa: {config.get('project', {}).get('base_normativa', 'ABNT NBR 9653:2018')}.", 58, badge_y + 8, 7.5, COLORS["muted"])
    c.setFillColor(COLORS["navy"])
    c.roundRect(badge_x, badge_y, badge_w, badge_h, 3, stroke=0, fill=1)
    _draw_text(c, config.get("project", {}).get("footer_badge", "DNA  •  ENAEX"), badge_x + 23, badge_y + 8, 8, "white", bold=True)
    c.setFillColor(COLORS["red"])
    c.rect(0, 0, PAGE_W, 6, fill=1, stroke=0)


def _first_page_layout() -> Dict[str, float]:
    first_card_y = FIRST_PAGE_LAST_CARD_Y + (FIRST_PAGE_CARD_SLOTS - 1) * (POINT_CARD_HEIGHT + POINT_CARD_GAP)
    points_title_y = first_card_y + POINT_CARD_HEIGHT + POINTS_TITLE_GAP
    return {
        "points_title_y": points_title_y,
        "first_card_y": first_card_y,
        "card_height": POINT_CARD_HEIGHT,
        "card_gap": POINT_CARD_GAP,
    }


def build_pdf_report(records: List[Dict], summary: Dict, config: Dict, charts: Dict[str, str], out_pdf: str | Path) -> Path:
    out_pdf = Path(out_pdf)
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(out_pdf), pagesize=A4)

    margin = 28
    layout = _first_page_layout()
    _draw_header(c, config, records, summary)
    _draw_text(c, "Resumo Executivo", margin, 652, 17, COLORS["text"])
    # Régua verde curta abaixo dos H1 — unifica com os headers das seções.
    c.setFillColor(COLORS["green"])
    c.rect(margin, 645, 42, 2, stroke=0, fill=1)
    _draw_scope(c, margin, 566, PAGE_W - 2 * margin, 72, config, records, summary)
    _draw_conclusion(c, margin, 488, PAGE_W - 2 * margin, 72, records, summary)

    _draw_text(c, "Pontos Monitorados", margin, layout["points_title_y"], 17, COLORS["text"])
    c.setFillColor(COLORS["green"])
    c.rect(margin, layout["points_title_y"] - 7, 42, 2, stroke=0, fill=1)
    y = layout["first_card_y"]
    card_h = layout["card_height"]
    for record in records[:FIRST_PAGE_CARD_SLOTS]:
        _draw_point_card(c, margin, y, PAGE_W - 2 * margin, card_h, record)
        y -= card_h + layout["card_gap"]
    if len(records) > FIRST_PAGE_CARD_SLOTS:
        _draw_text(c, f"+ {len(records) - FIRST_PAGE_CARD_SLOTS} ponto(s) adicionais no JSON consolidado.", margin + 10, y + 10, 8, COLORS["muted"])

    _draw_footer(c, config)
    c.showPage()

    _draw_chart_page(c, config, charts)
    c.showPage()

    # Páginas extras para campanhas com muitos pontos.
    if len(records) > FIRST_PAGE_CARD_SLOTS:
        remaining = records[FIRST_PAGE_CARD_SLOTS:]
        for idx in range(0, len(remaining), 8):
            batch = remaining[idx:idx + 8]
            _draw_text(c, "Pontos Monitorados - Continuação", margin, PAGE_H - 55, 17, COLORS["text"])
            yy = PAGE_H - 120
            for record in batch:
                _draw_point_card(c, margin, yy, PAGE_W - 2 * margin, card_h, record)
                yy -= card_h + 12
            _draw_footer(c, config)
            c.showPage()

    c.save()
    return out_pdf


def render_pdf_to_png(
    pdf_path: str | Path,
    out_png: str | Path,
    dpi: int = 300,
) -> Path:
    pdf_path = Path(pdf_path)
    out_png = Path(out_png)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(str(pdf_path))
    page = doc[0]
    pix = page.get_pixmap(dpi=dpi, alpha=False)
    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    image.save(out_png, format="PNG", optimize=True, dpi=(dpi, dpi))
    doc.close()
    return out_png
