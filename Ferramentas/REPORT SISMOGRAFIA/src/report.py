from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import fitz
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from .measurements import format_number, format_record_value


PAGE_W, PAGE_H = A4
FIRST_PAGE_CARD_SLOTS = 3
FIRST_PAGE_LAST_CARD_Y = 70
POINT_CARD_HEIGHT = 58
POINT_CARD_GAP = 14
POINTS_TITLE_GAP = 22
CHART_TO_POINTS_GAP = 16
CHARTS_TOP_LIMIT = 484
COLORS = {
    "red": "#E20613",
    "green": "#67C70A",  # Exclusivo para indicadores de conformidade.
    "dark": "#38424B",
    "navy": "#38424B",
    "text": "#111827",
    "muted": "#667085",
    "line": "#D9DEE7",
    "light_green": "#F7F8FA",
    "shadow": "#E1E5EA",
    "white": "#FFFFFF",
    "header_gray": "#E8EAEE",
    "missing": "#9AA1AC",
    "series_vertical": "#16A34A",
}


def _palette(config: Dict) -> Dict[str, str]:
    """Resolve the report palette from config, keeping green exclusive to status."""
    palette = config.get("branding", {}).get("palette", {})
    return {
        "red": palette.get("enaex_red", COLORS["red"]),
        "green": palette.get("status_conforme", COLORS["green"]),
        "dark": palette.get("enaex_gray", COLORS["dark"]),
        "navy": palette.get("enaex_gray", COLORS["navy"]),
        "text": palette.get("text", COLORS["text"]),
        "muted": palette.get("muted", COLORS["muted"]),
        "line": palette.get("gray_200", COLORS["line"]),
        "light_green": palette.get("gray_50", COLORS["light_green"]),
        "shadow": palette.get("gray_300", COLORS["shadow"]),
        "white": palette.get("white", COLORS["white"]),
        "header_gray": palette.get("gray_100", COLORS["header_gray"]),
        "missing": palette.get("status_ausente", COLORS["missing"]),
        "series_transversal": palette.get("series_transversal", COLORS["red"]),
        "series_longitudinal": palette.get("series_longitudinal", COLORS["dark"]),
        "series_vertical": palette.get("series_vertical", COLORS["series_vertical"]),
    }


def _report_layout(config: Dict | None = None) -> Dict[str, float]:
    """Resolve the configurable geometry used by every generated report."""
    layout = (config or {}).get("report_layout", {})
    return {
        "page_margin": float(layout.get("page_margin", 28.0)),
        "chart_column_gap": float(layout.get("chart_column_gap", 14.0)),
        "chart_inner_padding": float(layout.get("chart_inner_padding", 6.0)),
        "chart_header_height": float(layout.get("chart_header_height", 22.0)),
        "chart_to_points_gap": float(layout.get("chart_to_points_gap", CHART_TO_POINTS_GAP)),
        "charts_top_limit": float(layout.get("charts_top_limit", CHARTS_TOP_LIMIT)),
        "footer_height": float(layout.get("footer_height", 30.0)),
        "footer_accent_height": float(layout.get("footer_accent_height", 2.0)),
        "footer_side_padding": float(layout.get("footer_side_padding", 28.0)),
        "header_points_arrow_offset": float(layout.get("header_points_arrow_offset", 12.0)),
        "header_points_arrow_width": float(layout.get("header_points_arrow_width", 14.0)),
        "header_points_arrow_gap": float(layout.get("header_points_arrow_gap", 8.0)),
        "header_points_arrow_line_width": float(layout.get("header_points_arrow_line_width", 1.5)),
        "status_badge_width": float(layout.get("status_badge_width", 112.0)),
        "status_badge_height": float(layout.get("status_badge_height", 20.0)),
        "status_badge_radius": float(layout.get("status_badge_radius", 6.0)),
    }


def _report_text(config: Dict) -> Dict[str, str]:
    """Resolve labels in one place so future emissions share the same wording."""
    defaults = {
        "executive_title": "Resumo da Campanha Realizada",
        "scope_title": "Escopo da Campanha",
        "conclusion_title": "Conclusão Técnica",
        "points_title": "Pontos Monitorados",
        "continued_points_title": "Pontos Monitorados - Continuação",
        "pressure_chart_title": "Pressão Sonora x Distância",
        "vibration_chart_title": "PPV x Limite ABNT",
    }
    configured = config.get("report_text", {})
    return {key: str(configured.get(key, value)) for key, value in defaults.items()}


def fmt_num(value, digits=3, comma=True, qualifier=None):
    return format_number(value, digits=digits, comma=comma, qualifier=qualifier)


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


def _draw_round_rect(c: canvas.Canvas, x: float, y: float, w: float, h: float, radius: float = 5, fill: str = "#FFFFFF", stroke: str | None = None, shadow: bool = True, colors: Dict[str, str] = COLORS):
    if shadow:
        c.setFillColor(colors["shadow"])
        c.roundRect(x + 2, y - 2, w, h, radius, stroke=0, fill=1)
    c.setFillColor(fill)
    c.setStrokeColor(stroke or fill)
    c.roundRect(x, y, w, h, radius, stroke=1 if stroke else 0, fill=1)


def _section_header(c: canvas.Canvas, x: float, y: float, w: float, h: float, title: str, color: str | None = None, colors: Dict[str, str] = COLORS, align: str = "left"):
    color = color or colors["dark"]
    c.setFillColor(color)
    c.roundRect(x, y, w, h, 5, stroke=0, fill=1)
    c.setFillColor("white")
    c.setFont("Helvetica-Bold", 10)
    baseline = y + h - 13
    if align == "center":
        c.drawCentredString(x + w / 2, baseline, title)
    else:
        c.drawString(x + 12, baseline, title)


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


def _draw_header(c: canvas.Canvas, config: Dict, records: List[Dict], summary: Dict, colors: Dict[str, str]):
    layout = _report_layout(config)
    margin = layout["page_margin"]
    logo = Path(config.get("branding", {}).get("logo_path", "assets/enaex_logo.png"))
    if not logo.is_absolute():
        logo = Path(__file__).resolve().parents[1] / logo
    _fit_image(c, logo, margin, PAGE_H - 62, 112, 30)

    # Selo geométrico discreto: círculo com o número de pontos.
    c.setStrokeColor(colors["dark"])
    c.setLineWidth(1)
    c.circle(PAGE_W - 52, PAGE_H - 46, 14, stroke=1, fill=0)
    _draw_text(c, str(len(records)), PAGE_W - 55, PAGE_H - 50, 12, colors["dark"], bold=True)

    x, y, w, h = margin, PAGE_H - 144, PAGE_W - 2 * margin, 78
    _draw_round_rect(c, x, y, w, h, radius=5, fill=colors["white"], shadow=True, colors=colors)
    # Faixa superior discreta em cinza claro (troca do cinza médio anterior, menos pesado).
    c.setFillColor(colors["header_gray"])
    c.roundRect(x, y + h - 10, w, 10, 5, stroke=0, fill=1)

    _draw_text(c, config.get("project", {}).get("title", "MONITORAMENTO SISMOGRÁFICO"), x + 22, y + 46, 15, colors["red"], bold=True)
    client = summary.get("client") or config.get("project", {}).get("client_default", "US MINERAÇÃO VALE-VERDE")
    _draw_text(c, str(client).upper(), x + 22, y + 26, 11, "#697386", bold=True)
    point_count = f"{len(records)} ponto(s)"
    point_count_text_x = x + layout["header_points_arrow_offset"] + layout["header_points_arrow_width"] + layout["header_points_arrow_gap"]
    arrow_start_x = x + layout["header_points_arrow_offset"]
    arrow_tip_x = arrow_start_x + layout["header_points_arrow_width"]
    arrow_y = y + 14
    arrow_head = min(3.5, layout["header_points_arrow_width"] * 0.3)
    c.setStrokeColor(colors["red"])
    c.setFillColor(colors["red"])
    c.setLineWidth(layout["header_points_arrow_line_width"])
    c.line(arrow_start_x, arrow_y, arrow_tip_x - arrow_head, arrow_y)
    arrow = c.beginPath()
    arrow.moveTo(arrow_tip_x, arrow_y)
    arrow.lineTo(arrow_tip_x - arrow_head, arrow_y + arrow_head * 0.7)
    arrow.lineTo(arrow_tip_x - arrow_head, arrow_y - arrow_head * 0.7)
    arrow.close()
    c.drawPath(arrow, stroke=0, fill=1)
    _draw_text(c, point_count, point_count_text_x, y + 12, 8, colors["text"], bold=True)


def _draw_scope(c: canvas.Canvas, x: float, y: float, w: float, h: float, config: Dict, records: List[Dict], summary: Dict, colors: Dict[str, str]):
    labels = _report_text(config)
    _draw_round_rect(c, x, y, w, h, radius=5, fill=colors["white"], shadow=True, colors=colors)
    _section_header(c, x, y + h - 20, w, 20, labels["scope_title"], colors=colors)
    y0 = y + h - 32
    event_date = fmt_date_iso(summary.get("event_date"))
    client = summary.get("client") or config.get("project", {}).get("client_default", "N/D")
    _draw_text(c, f"Data do evento: {event_date}", x + 12, y0, 8)
    _draw_text(c, f"Cliente: {client}", x + 12, y0 - 11, 8)
    _draw_text(c, f"Pontos monitorados: {len(records)} fonte(s) de dados de sismógrafos processadas com sucesso.", x + 12, y0 - 22, 8)
    if config.get("report", {}).get("show_vibration_index", True):
        vib_limit = config.get("limits", {}).get("vibration_status_mm_s", 0.8)
        status = "abaixo" if summary.get("all_below_configured_vibration_limit") else "acima"
        status_color = colors["green"] if summary.get("all_below_configured_vibration_limit") else colors["red"]
        _draw_text(c, f"■ Índices de vibração: {status} de {str(vib_limit).replace('.', ',')} mm/s.", x + 12, y0 - 33, 8, status_color, bold=True)


def _draw_conclusion(c: canvas.Canvas, x: float, y: float, w: float, h: float, records: List[Dict], summary: Dict, config: Dict, colors: Dict[str, str]):
    labels = _report_text(config)
    _draw_round_rect(c, x, y, w, h, radius=5, fill=colors["white"], shadow=True, colors=colors)
    _section_header(c, x, y + h - 20, w, 20, labels["conclusion_title"], colors=colors)

    rows = [
        ("Conformidade", "Todos os pontos abaixo dos limites da ABNT NBR 9653:2018." if summary.get("all_conforme_abnt") else "Há ponto(s) acima de limite ou com dado ausente para avaliação."),
        ("Maior PSPL", f"{fmt_num(summary.get('max_pspl', {}).get('value_db'), 1, qualifier=summary.get('max_pspl', {}).get('qualifier'))} dB(L) | {summary.get('max_pspl', {}).get('point_name') or 'N/D'}"),
        ("Maior PPV", f"{fmt_num(summary.get('max_ppv', {}).get('value_mm_s'), 3, qualifier=summary.get('max_ppv', {}).get('qualifier'))} mm/s | {summary.get('max_ppv', {}).get('point_name') or 'N/D'}"),
        ("Maior PVS", f"{fmt_num(summary.get('max_pvs', {}).get('value_mm_s'), 3, qualifier=summary.get('max_pvs', {}).get('qualifier'))} mm/s | {summary.get('max_pvs', {}).get('point_name') or 'N/D'}"),
    ]
    table_x, table_y = x + 12, y + 8
    row_h = 11
    col1 = 88
    total_w = w - 24
    for i, (label, value) in enumerate(rows):
        yy = table_y + (len(rows) - 1 - i) * row_h
        # Faixa de rótulo em verde-claro (sem bordas); linha separadora sutil abaixo.
        c.setFillColor(colors["light_green"])
        c.rect(table_x, yy, col1, row_h, fill=1, stroke=0)
        if i < len(rows) - 1:
            c.setStrokeColor(colors["line"])
            c.setLineWidth(0.4)
            c.line(table_x + col1, yy, table_x + total_w, yy)
        _draw_text(c, label, table_x + 6, yy + 3, 7, colors["text"], bold=True)
        _draw_text(c, value, table_x + col1 + 6, yy + 3, 7, colors["text"])


def _draw_chart_card(c: canvas.Canvas, x: float, y: float, w: float, h: float, title: str, image_path: str, colors: Dict[str, str], layout: Dict[str, float]):
    _draw_round_rect(c, x, y, w, h, radius=5, fill=colors["white"], shadow=True, colors=colors)
    header_h = layout["chart_header_height"]
    padding = layout["chart_inner_padding"]
    _section_header(c, x, y + h - header_h, w, header_h, title, colors=colors, align="center")
    _fit_image(c, image_path, x + padding, y + padding, w - 2 * padding, h - header_h - 2 * padding)


def _point_status_text(record: Dict, colors: Dict[str, str] = COLORS) -> Tuple[str, str]:
    ok = record.get("evaluation", {}).get("overall_conforme_abnt")
    if ok is True:
        return "CONFORME ABNT", colors["green"]
    if ok is False:
        return "VERIFICAR", colors["red"]
    return "DADO AUSENTE", colors["missing"]


def _point_accent_color(record: Dict, colors: Dict[str, str] = COLORS) -> str:
    """Resolve the semantic color used by the status badge."""
    return _point_status_text(record, colors)[1]


def _draw_status_badge(c: canvas.Canvas, x: float, y: float, w: float, h: float, label: str, color: str, colors: Dict[str, str], radius: float = 6.0):
    """Draw a compact status lock-up with an icon instead of a generic flat pill."""
    radius = min(radius, h / 2)
    c.setFillColor(color)
    c.roundRect(x, y, w, h, radius, stroke=0, fill=1)

    icon_x = x + 13
    icon_y = y + h / 2
    c.setFillColor(colors["white"])
    c.circle(icon_x, icon_y, 5.2, stroke=0, fill=1)
    c.setStrokeColor(color)
    c.setLineWidth(1.1)
    if label == "CONFORME ABNT":
        c.line(icon_x - 2.7, icon_y, icon_x - 0.7, icon_y - 2.0)
        c.line(icon_x - 0.7, icon_y - 2.0, icon_x + 3.0, icon_y + 2.4)
    elif label == "VERIFICAR":
        c.line(icon_x, icon_y - 2.4, icon_x, icon_y + 2.0)
        c.circle(icon_x, icon_y - 3.4, 0.55, stroke=1, fill=0)
    else:
        c.line(icon_x - 2.5, icon_y, icon_x + 2.5, icon_y)

    _draw_text(c, label, x + 23, y + (h - 7.5) / 2 + 2.0, 7.5, colors["white"], bold=True)


def _draw_point_card(c: canvas.Canvas, x: float, y: float, w: float, h: float, record: Dict, colors: Dict[str, str], layout: Dict[str, float] | None = None):
    layout = layout or _report_layout({})
    _draw_round_rect(c, x, y, w, h, radius=5, fill=colors["white"], shadow=True, colors=colors)
    c.setFillColor(colors["dark"])
    c.roundRect(x, y + h - 17, w, 17, 4, stroke=0, fill=1)
    _draw_text(c, str(record.get("point_name", "PONTO MONITORADO")).upper(), x + 12, y + h - 12, 9, "white", bold=True)

    table_x = x + 12
    table_y = y + 7
    row_h = 11
    label_w = 42
    col_pairs = [
        [("Data", fmt_date_iso(record.get("event_date"))), ("PSPL", f"{format_record_value(record, 'pspl_db', 1)} dB(L)"), ("Mic", f"{format_record_value(record, 'mic_freq_hz', 1)} Hz")],
        [("PVS", f"{format_record_value(record, 'pvs_mm_s', 3)} mm/s"), ("SD", format_record_value(record, 'scaled_distance', 1)), ("Dist / Carga", f"{format_record_value(record, 'gps_distance_m', 1)} m | {format_record_value(record, 'charge_kg', 1)} kg")],
        [("Tran", f"{format_record_value(record, 'tran_ppv_mm_s', 3)} mm/s | {format_record_value(record, 'tran_freq_hz', 1)} Hz"), ("Vert", f"{format_record_value(record, 'vert_ppv_mm_s', 3)} mm/s | {format_record_value(record, 'vert_freq_hz', 1)} Hz"), ("Long", f"{format_record_value(record, 'long_ppv_mm_s', 3)} mm/s | {format_record_value(record, 'long_freq_hz', 1)} Hz")],
    ]
    # Renderiza em três blocos horizontais, cada bloco com 3 linhas.
    block_w = 135
    for block_idx, rows in enumerate(col_pairs):
        bx = table_x + block_idx * (block_w + 5)
        for i, (label, value) in enumerate(rows):
            yy = table_y + (2 - i) * row_h
            c.setFillColor(colors["light_green"])
            c.rect(bx, yy, label_w, row_h, fill=1, stroke=0)
            if i < 2:
                c.setStrokeColor(colors["line"])
                c.setLineWidth(0.35)
                c.line(bx + label_w, yy, bx + block_w, yy)
            _draw_text(c, label, bx + 5, yy + 3, 5.8, colors["text"], bold=True)
            _draw_text(c, value, bx + label_w + 5, yy + 3, 5.8, colors["text"])

    label, color = _point_status_text(record, colors)
    btn_w = layout["status_badge_width"]
    btn_h = layout["status_badge_height"]
    _draw_status_badge(
        c,
        x + w - btn_w - 12,
        y + 12,
        btn_w,
        btn_h,
        label,
        color,
        colors,
        radius=layout["status_badge_radius"],
    )


def _draw_footer(c: canvas.Canvas, config: Dict, colors: Dict[str, str]):
    layout = _report_layout(config)
    footer_h = layout["footer_height"]
    accent_h = min(layout["footer_accent_height"], footer_h / 2)
    side = layout["footer_side_padding"]
    c.setFillColor(colors["navy"])
    c.rect(0, 0, PAGE_W, footer_h, stroke=0, fill=1)
    c.setFillColor(colors["red"])
    c.rect(0, footer_h - accent_h, PAGE_W, accent_h, stroke=0, fill=1)

    base = config.get("project", {}).get("base_normativa", "ABNT NBR 9653:2018")
    _draw_text(c, f"Base normativa: {base}", side, 10.5, 7.5, colors["white"])
    c.setStrokeColor(colors["header_gray"])
    c.setLineWidth(0.6)
    c.line(PAGE_W - 148, 8, PAGE_W - 148, footer_h - 8)
    c.setFillColor(colors["white"])
    c.setFont("Helvetica-Bold", 8.5)
    c.drawRightString(PAGE_W - side, 10.5, str(config.get("project", {}).get("footer_badge", "DNA  •  ENAEX")))


def _first_page_layout(config: Dict | None = None) -> Dict[str, float]:
    report_layout = _report_layout(config)
    first_card_y = FIRST_PAGE_LAST_CARD_Y + (FIRST_PAGE_CARD_SLOTS - 1) * (POINT_CARD_HEIGHT + POINT_CARD_GAP)
    points_title_y = first_card_y + POINT_CARD_HEIGHT + POINTS_TITLE_GAP
    chart_y = points_title_y + report_layout["chart_to_points_gap"]
    chart_h = report_layout["charts_top_limit"] - chart_y
    if chart_h <= 0:
        raise ValueError("Invalid first-page layout: chart height must stay positive.")
    return {
        "points_title_y": points_title_y,
        "first_card_y": first_card_y,
        "card_height": POINT_CARD_HEIGHT,
        "card_gap": POINT_CARD_GAP,
        "chart_y": chart_y,
        "chart_h": chart_h,
        "chart_to_points_gap": report_layout["chart_to_points_gap"],
        "charts_top_limit": report_layout["charts_top_limit"],
    }


def build_pdf_report(records: List[Dict], summary: Dict, config: Dict, charts: Dict[str, str], out_pdf: str | Path) -> Path:
    out_pdf = Path(out_pdf)
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(out_pdf), pagesize=A4)
    colors = _palette(config)

    report_layout = _report_layout(config)
    labels = _report_text(config)
    margin = report_layout["page_margin"]
    layout = _first_page_layout(config)
    _draw_header(c, config, records, summary, colors)
    _draw_text(c, labels["executive_title"], margin, 652, 17, colors["text"])
    c.setFillColor(colors["red"])
    c.rect(margin, 645, 42, 2, stroke=0, fill=1)
    _draw_scope(c, margin, 566, PAGE_W - 2 * margin, 72, config, records, summary, colors)
    _draw_conclusion(c, margin, 488, PAGE_W - 2 * margin, 72, records, summary, config, colors)

    chart_gap = report_layout["chart_column_gap"]
    chart_w = (PAGE_W - 2 * margin - chart_gap) / 2
    _draw_chart_card(c, margin, layout["chart_y"], chart_w, layout["chart_h"], labels["pressure_chart_title"], charts["pressure_chart"], colors, report_layout)
    _draw_chart_card(c, margin + chart_w + chart_gap, layout["chart_y"], chart_w, layout["chart_h"], labels["vibration_chart_title"], charts["vibration_chart"], colors, report_layout)

    _draw_text(c, labels["points_title"], margin, layout["points_title_y"], 17, colors["text"])
    c.setFillColor(colors["red"])
    c.rect(margin, layout["points_title_y"] - 7, 42, 2, stroke=0, fill=1)
    y = layout["first_card_y"]
    card_h = layout["card_height"]
    for record in records[:FIRST_PAGE_CARD_SLOTS]:
        _draw_point_card(c, margin, y, PAGE_W - 2 * margin, card_h, record, colors, report_layout)
        y -= card_h + layout["card_gap"]
    if len(records) > FIRST_PAGE_CARD_SLOTS:
        _draw_text(c, f"+ {len(records) - FIRST_PAGE_CARD_SLOTS} ponto(s) adicionais no JSON consolidado.", margin + 10, y + 10, 8, COLORS["muted"])

    _draw_footer(c, config, colors)
    c.showPage()

    # Páginas extras para campanhas com muitos pontos.
    if len(records) > FIRST_PAGE_CARD_SLOTS:
        remaining = records[FIRST_PAGE_CARD_SLOTS:]
        for idx in range(0, len(remaining), 8):
            batch = remaining[idx:idx + 8]
            _draw_text(c, labels["continued_points_title"], margin, PAGE_H - 55, 17, colors["text"])
            yy = PAGE_H - 120
            for record in batch:
                _draw_point_card(c, margin, yy, PAGE_W - 2 * margin, card_h, record, colors, report_layout)
                yy -= card_h + 12
            _draw_footer(c, config, colors)
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
