from __future__ import annotations

from typing import Dict, List

from .measurements import format_record_value


def fmt_num(value, digits=3):
    if value is None:
        return "N/D"
    return f"{float(value):.{digits}f}".replace('.', ',')


def fmt_date(value: str | None) -> str:
    if not value:
        return "N/D"
    parts = str(value).split('-')
    if len(parts) == 3:
        return f"{parts[2]}/{parts[1]}/{parts[0]}"
    return str(value)


def _fmt_limit(value) -> str:
    if value is None:
        return "N/D"
    return str(value).replace(".", ",")


def build_whatsapp_note(records: List[Dict], summary: Dict, config: Dict) -> str:
    vib_limit = config.get("limits", {}).get("vibration_status_mm_s", 0.8)
    event_date = fmt_date(summary.get("event_date"))
    client = summary.get("client") or config.get("project", {}).get("client_default") or "N/D"
    base_normativa = config.get("project", {}).get("base_normativa", "NBR 9653:2018")

    over_limit_points = [
        record.get("point_name") or "N/D"
        for record in records
        if record.get("evaluation", {}).get("vibration_status_ok") is False
    ]
    below_limit = summary.get("all_below_configured_vibration_limit")

    if below_limit is False:
        vibration_status = f"⚠️ Índices de vibração: acima de {_fmt_limit(vib_limit)} mm/s. Pontos: {', '.join(over_limit_points) if over_limit_points else 'N/D'}."
        status_final = f"⚠️ *STATUS:* Verificar pontos acima do limite da *{base_normativa}*."
    elif below_limit is True:
        vibration_status = f"✅ Índices de vibração: abaixo de {_fmt_limit(vib_limit)} mm/s."
        status_final = f"✅ *STATUS:* Todos os parâmetros estão em conformidade com a *{base_normativa}*."
    else:
        vibration_status = "⚠️ Índices de vibração: dados insuficientes para avaliação."
        status_final = f"⚠️ *STATUS:* Verificar dados ausentes para a *{base_normativa}*."

    point_lines: List[str] = []
    for record in records:
        point_lines.extend(
            [
                f" *{record.get('point_name') or 'N/D'}*",
                f"   • PVS: {format_record_value(record, 'pvs_mm_s', 3)} mm/s",
                f"   • PSPL: {format_record_value(record, 'pspl_db', 1)} dB(L)",
                "",
            ]
        )
    if point_lines:
        point_lines.pop()

    lines = [
        "*MONITORAMENTO SISMOGRÁFICO — ENAEX*",
        "",
        f"*Cliente:* {client}",
        f"*Data:* {event_date}",
        "",
        vibration_status,
        "",
        *point_lines,
        "",
        status_final,
    ]
    return "\n".join(lines)
