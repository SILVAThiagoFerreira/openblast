from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

from .artifacts import resolve_artifact_name
from .compliance import interpolate_limit


COLORS = {
    "dark": "#2F3440",
    "red": "#E30613",
    "green": "#67C70A",
    "blue": "#2D7DBF",
    "gray": "#6B7280",
}

FIGSIZE = (6.5, 4.55)


def _safe_name(name: str) -> str:
    return str(name).replace("COMUNIDADE DE ", "Com. ").title()


def _annotation_candidates(x: float, xmid: float) -> List[tuple[float, float, str, str]]:
    """Retorna offsets candidatos em pontos, priorizando o lado mais livre do gráfico."""
    if x <= xmid:
        return [
            (14.0, 14.0, "left", "bottom"),
            (14.0, -18.0, "left", "top"),
            (-14.0, 14.0, "right", "bottom"),
            (-14.0, -18.0, "right", "top"),
            (24.0, 20.0, "left", "bottom"),
            (24.0, -24.0, "left", "top"),
            (-24.0, 20.0, "right", "bottom"),
            (-24.0, -24.0, "right", "top"),
        ]
    return [
        (-14.0, 14.0, "right", "bottom"),
        (-14.0, -18.0, "right", "top"),
        (14.0, 14.0, "left", "bottom"),
        (14.0, -18.0, "left", "top"),
        (-24.0, 20.0, "right", "bottom"),
        (-24.0, -24.0, "right", "top"),
        (24.0, 20.0, "left", "bottom"),
        (24.0, -24.0, "left", "top"),
    ]


def _estimate_text_box(text: str, fontsize: float, dpi: float, pad_px: float = 4.0) -> tuple[float, float]:
    lines = str(text).splitlines() or [""]
    max_chars = max((len(line) for line in lines), default=0)
    char_width = fontsize * dpi / 72.0 * 0.58
    line_height = fontsize * dpi / 72.0 * 1.18
    width = max_chars * char_width + pad_px * 2.0
    height = len(lines) * line_height + pad_px * 2.0
    return width, height


def _rect_overlap_area(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return 0.0
    return (x1 - x0) * (y1 - y0)


def _build_bbox(
    point_disp: tuple[float, float],
    text: str,
    fontsize: float,
    dpi: float,
    dx_pt: float,
    dy_pt: float,
    ha: str,
    va: str,
) -> tuple[float, float, float, float]:
    dx = dx_pt * dpi / 72.0
    dy = dy_pt * dpi / 72.0
    anchor_x = point_disp[0] + dx
    anchor_y = point_disp[1] + dy
    width, height = _estimate_text_box(text, fontsize, dpi)

    if ha == "center":
        x0 = anchor_x - width / 2.0
    elif ha == "right":
        x0 = anchor_x - width
    else:
        x0 = anchor_x

    if va == "center":
        y0 = anchor_y - height / 2.0
    elif va == "top":
        y0 = anchor_y - height
    else:
        y0 = anchor_y

    return (x0, y0, x0 + width, y0 + height)


def _pick_annotation(
    ax,
    x: float,
    y: float,
    text: str,
    used_boxes: List[tuple[float, float, float, float]],
    fontsize: float,
    renderer,
) -> tuple[float, float, str, str]:
    point_disp = ax.transData.transform((x, y))
    xmid = sum(ax.get_xlim()) / 2.0
    axes_box = ax.get_window_extent(renderer=renderer)
    candidates = _annotation_candidates(x, xmid)

    best = None
    best_score = None
    for dx_pt, dy_pt, ha, va in candidates:
        bbox = _build_bbox(point_disp, text, fontsize, ax.figure.dpi, dx_pt, dy_pt, ha, va)
        overlap = sum(_rect_overlap_area(bbox, used) for used in used_boxes)
        outside_penalty = 0.0
        if bbox[0] < axes_box.x0 - 4:
            outside_penalty += (axes_box.x0 - 4 - bbox[0]) * 4.0
        if bbox[1] < axes_box.y0 - 4:
            outside_penalty += (axes_box.y0 - 4 - bbox[1]) * 4.0
        if bbox[2] > axes_box.x1 + 4:
            outside_penalty += (bbox[2] - axes_box.x1 - 4) * 4.0
        if bbox[3] > axes_box.y1 + 4:
            outside_penalty += (bbox[3] - axes_box.y1 - 4) * 4.0
        score = overlap + outside_penalty
        if best is None or score < best_score:
            best = (dx_pt, dy_pt, ha, va)
            best_score = score
        if score == 0:
            return best

    return best if best is not None else candidates[0]


def _annotate_points(ax, items: List[Dict], fontsize: float = 6.2) -> None:
    fig = ax.figure
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    used_boxes: List[tuple[float, float, float, float]] = []

    for item in items:
        x = item.get("x")
        y = item.get("y")
        text = item.get("text")
        if x is None or y is None or not text:
            continue
        dx_pt, dy_pt, ha, va = _pick_annotation(ax, x, y, text, used_boxes, fontsize, renderer)
        point_disp = ax.transData.transform((x, y))
        bbox = _build_bbox(point_disp, text, fontsize, fig.dpi, dx_pt, dy_pt, ha, va)
        used_boxes.append(bbox)
        ax.annotate(
            text,
            (x, y),
            textcoords="offset points",
            xytext=(dx_pt, dy_pt),
            ha=ha,
            va=va,
            fontsize=fontsize,
            color=COLORS["gray"],
            bbox=dict(boxstyle="round,pad=0.16", fc="white", ec="#CBD5E1", lw=0.55),
            arrowprops=dict(arrowstyle="-", color="#94A3B8", lw=0.45, shrinkA=0, shrinkB=4),
            zorder=5,
        )


def make_pressure_chart(records: List[Dict], config: Dict, out_path: str | Path) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    limit = float(config.get("limits", {}).get("sound_pressure_db", 134.0))
    chart_cfg = config.get("charts", {})

    xs = [r.get("gps_distance_m") for r in records if r.get("gps_distance_m") is not None and r.get("pspl_db") is not None]
    ys = [r.get("pspl_db") for r in records if r.get("gps_distance_m") is not None and r.get("pspl_db") is not None]
    max_x = max(xs) if xs else 1000
    x_max = max(max_x * 1.25, 2000)
    y_max = float(chart_cfg.get("pressure_y_max", 160.0))

    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=220)
    ax.set_title("Pressão Sonora em Eventos Sismográficos - ABNT NBR 9653:2018", fontsize=8, pad=12)
    ax.axhline(limit, color=COLORS["dark"], linewidth=1.8, label=f"Limite de {limit:g} dB")
    ax.scatter(xs, ys, s=28, color=COLORS["red"], label="Pressão Sonora (dB)", zorder=3)

    label_items = []
    for idx, r in enumerate(sorted(records, key=lambda rec: (rec.get("gps_distance_m") is None, rec.get("gps_distance_m") or 0.0))):
        x = r.get("gps_distance_m")
        y = r.get("pspl_db")
        if x is None or y is None:
            continue
        label_items.append({
            "x": x,
            "y": y,
            "text": f"{_safe_name(r.get('point_name', 'Ponto'))}\n{y:.1f}",
            "index": idx,
        })

    ax.set_xlim(float(chart_cfg.get("pressure_x_min", 0.0)), x_max)
    ax.set_ylim(float(chart_cfg.get("pressure_y_min", 0.0)), y_max)
    ax.set_xlabel("Distância (m)", fontsize=7, labelpad=8)
    ax.set_ylabel("Pressão Acústica (dB)", fontsize=7)
    ax.grid(True, linewidth=0.35, color="#B7BDC7", alpha=0.9)
    ax.tick_params(axis="both", labelsize=6)
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False, fontsize=6)
    _annotate_points(ax, label_items, fontsize=6.0)
    fig.tight_layout(pad=1.2)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


def _curve_points_for_xmax(curve, xmax):
    pts = sorted((float(x), float(y)) for x, y in curve)
    selected = []
    for x, y in pts:
        if x <= xmax:
            selected.append((x, y))
    if not selected or selected[-1][0] < xmax:
        selected.append((xmax, interpolate_limit(xmax, curve)))
    return selected


def make_vibration_chart(records: List[Dict], config: Dict, out_path: str | Path) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    curve = config.get("limits", {}).get("nbr9653_curve", [[0, 15], [4, 15], [15, 20], [40, 50], [1000, 50]])
    chart_cfg = config.get("charts", {})
    y_tick_step = float(chart_cfg.get("vibration_y_tick_step", 0.1))
    use_broken_y = bool(chart_cfg.get("vibration_use_broken_y", True))
    focus_y_max = float(chart_cfg.get("vibration_y_focus_max", 1.0))

    axes = [
        ("Transversal", "tran_ppv_mm_s", "tran_freq_hz", "s", COLORS["red"]),
        ("Longitudinal", "long_ppv_mm_s", "long_freq_hz", "D", "#1D4ED8"),
        ("Vertical", "vert_ppv_mm_s", "vert_freq_hz", "^", "#16A34A"),
    ]
    freqs = []
    ppvs = []
    for r in records:
        for _, ppv_key, freq_key, _, _ in axes:
            if r.get(freq_key) is not None and r.get(ppv_key) is not None:
                freqs.append(r.get(freq_key))
                ppvs.append(r.get(ppv_key))
    max_freq = max(freqs) if freqs else 60.0
    max_ppv = max(ppvs) if ppvs else 1.0
    x_max = max(float(chart_cfg.get("vibration_x_max_minimum", 60.0)), max_freq * 1.35)
    y_max = max(float(chart_cfg.get("vibration_y_max_minimum", 60.0)), max_ppv * 1.35)

    curve_pts = _curve_points_for_xmax(curve, x_max)
    curve_ys = [p[1] for p in curve_pts]
    curve_y_min = min(curve_ys) if curve_ys else 15.0
    curve_y_max = max(curve_ys) if curve_ys else 50.0
    should_break_y = use_broken_y and max_ppv < curve_y_min * 0.25

    if should_break_y:
        y_focus_max = max(focus_y_max, max_ppv * 1.35, y_tick_step * 5)
        fig, (ax_top, ax) = plt.subplots(
            2,
            1,
            sharex=True,
            figsize=FIGSIZE,
            dpi=220,
            gridspec_kw={"height_ratios": [1.0, 1.25], "hspace": 0.08},
        )
        ax_top.set_title("Vibração em Eventos Sismográficos - ABNT NBR 9653:2018", fontsize=8, pad=12)
        ax_top.plot([p[0] for p in curve_pts], [p[1] for p in curve_pts], color=COLORS["dark"], linewidth=1.8, label="Limite ABNT")
        ax_top.set_ylim(max(0.0, curve_y_min - 2.0), curve_y_max + 5.0)
        ax_top.set_xlim(float(chart_cfg.get("vibration_x_min", 0.0)), x_max)
        ax_top.grid(True, linewidth=0.35, color="#B7BDC7", alpha=0.9)
        ax_top.tick_params(axis="both", labelsize=6)
        ax_top.spines["bottom"].set_visible(False)
        ax_top.tick_params(labelbottom=False)

        # Guias visuais nos pontos principais da curva, preservando a leitura da NBR.
        top_y_min, top_y_max = ax_top.get_ylim()
        for x, y in curve_pts[1:-1]:
            if x <= x_max and top_y_min <= y <= top_y_max:
                ax.axvline(x, color=COLORS["red"], linewidth=0.8, linestyle=(0, (5, 4)), alpha=0.85)
                ax_top.axvline(x, ymin=0, ymax=(y - top_y_min) / (top_y_max - top_y_min), color=COLORS["red"], linewidth=0.8, linestyle=(0, (5, 4)), alpha=0.85)
                ax_top.axhline(y, xmin=0, xmax=x / x_max, color=COLORS["red"], linewidth=0.8, linestyle=(0, (5, 4)), alpha=0.85)

        ax.set_ylim(float(chart_cfg.get("vibration_y_min", 0.0)), y_focus_max)
        ax.spines["top"].set_visible(False)

        d = 0.012
        kwargs = dict(transform=ax_top.transAxes, color=COLORS["dark"], clip_on=False, linewidth=0.8)
        ax_top.plot((-d, +d), (-d, +d), **kwargs)
        ax_top.plot((1 - d, 1 + d), (-d, +d), **kwargs)
        kwargs.update(transform=ax.transAxes)
        ax.plot((-d, +d), (1 - d, 1 + d), **kwargs)
        ax.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)
    else:
        fig, ax = plt.subplots(figsize=FIGSIZE, dpi=220)
        ax.set_title("Vibração em Eventos Sismográficos - ABNT NBR 9653:2018", fontsize=8, pad=12)
        ax.plot([p[0] for p in curve_pts], [p[1] for p in curve_pts], color=COLORS["dark"], linewidth=1.8, label="Limite ABNT")

        # Guias visuais nos pontos principais da curva.
        for x, y in curve_pts[1:-1]:
            if x <= x_max and y <= y_max:
                ax.axvline(x, ymin=0, ymax=y / y_max, color=COLORS["red"], linewidth=0.8, linestyle=(0, (5, 4)), alpha=0.85)
                ax.axhline(y, xmin=0, xmax=x / x_max, color=COLORS["red"], linewidth=0.8, linestyle=(0, (5, 4)), alpha=0.85)
        ax.set_ylim(float(chart_cfg.get("vibration_y_min", 0.0)), y_max)

    for label, ppv_key, freq_key, marker, color in axes:
        xs, ys = [], []
        for r in records:
            if r.get(freq_key) is not None and r.get(ppv_key) is not None:
                xs.append(r.get(freq_key))
                ys.append(r.get(ppv_key))
        ax.scatter(xs, ys, s=32, marker=marker, color=color, label=f"{label} (mm/s)", zorder=4)

    # Anota apenas o maior eixo de cada ponto para manter o gráfico limpo.
    label_items = []
    for idx, r in enumerate(sorted(records, key=lambda rec: (rec.get("evaluation", {}).get("ppv_max_freq_hz") is None, rec.get("evaluation", {}).get("ppv_max_freq_hz") or 0.0))):
        ev = r.get("evaluation", {})
        freq = ev.get("ppv_max_freq_hz")
        ppv = ev.get("ppv_max_mm_s")
        if freq is None or ppv is None:
            continue
        label_items.append({
            "x": freq,
            "y": ppv,
            "text": _safe_name(r.get("point_name", "Ponto")),
            "index": idx,
        })

    ax.set_xlim(float(chart_cfg.get("vibration_x_min", 0.0)), x_max)
    if y_tick_step > 0:
        if should_break_y:
            ax.yaxis.set_major_locator(MultipleLocator(y_tick_step))
        else:
            ax.yaxis.set_minor_locator(MultipleLocator(y_tick_step))
        if not should_break_y and y_max <= 5:
            ax.yaxis.set_major_locator(MultipleLocator(y_tick_step))
    ax.set_xlabel("Frequência (Hz)", fontsize=7, labelpad=8)
    ax.set_ylabel("PPV (mm/s)", fontsize=7)
    ax.grid(True, linewidth=0.35, color="#B7BDC7", alpha=0.9)
    ax.grid(True, which="minor", axis="y", linewidth=0.2, color="#D7DCE5", alpha=0.35)
    ax.tick_params(axis="both", labelsize=6)
    if should_break_y:
        handles_top, labels_top = ax_top.get_legend_handles_labels()
        handles_bottom, labels_bottom = ax.get_legend_handles_labels()
        ax_top.legend(handles_top + handles_bottom, labels_top + labels_bottom, loc="center left", bbox_to_anchor=(1.02, -0.15), frameon=False, fontsize=6)
    else:
        ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False, fontsize=6)
    _annotate_points(ax, label_items, fontsize=5.9)
    if should_break_y:
        fig.subplots_adjust(left=0.10, right=0.78, top=0.88, bottom=0.14, hspace=0.08)
    else:
        fig.tight_layout(pad=1.2)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


def make_all_charts(records: List[Dict], config: Dict, out_dir: str | Path, artifact_context: Dict[str, str]) -> Dict[str, str]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    pressure_name = resolve_artifact_name(config, "pressure_chart", artifact_context)
    vibration_name = resolve_artifact_name(config, "vibration_chart", artifact_context)
    pressure = make_pressure_chart(records, config, out_dir / pressure_name)
    vibration = make_vibration_chart(records, config, out_dir / vibration_name)
    return {"pressure_chart": str(pressure), "vibration_chart": str(vibration)}
