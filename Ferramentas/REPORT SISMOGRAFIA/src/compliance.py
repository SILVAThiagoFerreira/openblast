from __future__ import annotations

from typing import Dict, List, Optional, Tuple


def interpolate_limit(freq_hz: Optional[float], curve: List[List[float]]) -> Optional[float]:
    if freq_hz is None:
        return None
    if not curve:
        return None
    points = sorted((float(x), float(y)) for x, y in curve)
    x = float(freq_hz)
    if x <= points[0][0]:
        return points[0][1]
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if x0 <= x <= x1:
            if x1 == x0:
                return y1
            t = (x - x0) / (x1 - x0)
            return y0 + t * (y1 - y0)
    return points[-1][1]


def _axis_values(record: Dict) -> List[Tuple[str, Optional[float], Optional[float]]]:
    return [
        ("Tran", record.get("tran_ppv_mm_s"), record.get("tran_freq_hz")),
        ("Vert", record.get("vert_ppv_mm_s"), record.get("vert_freq_hz")),
        ("Long", record.get("long_ppv_mm_s"), record.get("long_freq_hz")),
    ]


def evaluate_record(record: Dict, config: Dict) -> Dict:
    limits = config.get("limits", {})
    curve = limits.get("nbr9653_curve", [[0, 15], [4, 15], [15, 20], [40, 50], [1000, 50]])
    pspl_limit = float(limits.get("sound_pressure_db", 134.0))
    vibration_status_limit = float(limits.get("vibration_status_mm_s", 0.8))

    axes = []
    for axis, ppv, freq in _axis_values(record):
        lim = interpolate_limit(freq, curve)
        conforming = None if ppv is None or lim is None else ppv <= lim
        axes.append({
            "axis": axis,
            "ppv_mm_s": ppv,
            "freq_hz": freq,
            "nbr9653_limit_mm_s": lim,
            "conforme_nbr9653": conforming,
        })

    numeric_ppvs = [a["ppv_mm_s"] for a in axes if a["ppv_mm_s"] is not None]
    ppv_max = max(numeric_ppvs) if numeric_ppvs else None
    ppv_max_axis = None
    ppv_max_freq = None
    if ppv_max is not None:
        for a in axes:
            if a["ppv_mm_s"] == ppv_max:
                ppv_max_axis = a["axis"]
                ppv_max_freq = a["freq_hz"]
                break

    pvs = record.get("pvs_mm_s")
    candidates = [v for v in [ppv_max, pvs] if v is not None]
    vibration_index = max(candidates) if candidates else None

    pspl = record.get("pspl_db")
    sound_ok = None if pspl is None else pspl <= pspl_limit
    vibration_status_ok = None if vibration_index is None else vibration_index <= vibration_status_limit
    nbr_axis_checks = [a["conforme_nbr9653"] for a in axes if a["conforme_nbr9653"] is not None]
    nbr_vibration_ok = all(nbr_axis_checks) if nbr_axis_checks else None

    overall_checks = [x for x in [sound_ok, nbr_vibration_ok] if x is not None]
    overall_ok = all(overall_checks) if overall_checks else None

    record["evaluation"] = {
        "axis_results": axes,
        "ppv_max_mm_s": ppv_max,
        "ppv_max_axis": ppv_max_axis,
        "ppv_max_freq_hz": ppv_max_freq,
        "vibration_index_mm_s": vibration_index,
        "vibration_status_limit_mm_s": vibration_status_limit,
        "vibration_status_ok": vibration_status_ok,
        "sound_pressure_limit_db": pspl_limit,
        "sound_ok": sound_ok,
        "nbr_vibration_ok": nbr_vibration_ok,
        "overall_conforme_abnt": overall_ok,
    }
    return record


def evaluate_records(records: List[Dict], config: Dict) -> List[Dict]:
    return [evaluate_record(dict(r), config) for r in records]


def campaign_summary(records: List[Dict], config: Dict) -> Dict:
    evals = [r.get("evaluation", {}) for r in records]
    max_pspl_record = max(records, key=lambda r: (r.get("pspl_db") is not None, r.get("pspl_db") or -1), default=None)
    max_ppv_record = max(records, key=lambda r: (r.get("evaluation", {}).get("ppv_max_mm_s") is not None, r.get("evaluation", {}).get("ppv_max_mm_s") or -1), default=None)
    max_pvs_record = max(records, key=lambda r: (r.get("pvs_mm_s") is not None, r.get("pvs_mm_s") or -1), default=None)

    overall_values = [e.get("overall_conforme_abnt") for e in evals if e.get("overall_conforme_abnt") is not None]
    vibration_status_values = [e.get("vibration_status_ok") for e in evals if e.get("vibration_status_ok") is not None]

    project_cfg = config.get("project", {})
    client_display = project_cfg.get("client_override")
    if not client_display and records:
        client_display = records[0].get("client") or records[0].get("company")
    if not client_display:
        client_display = project_cfg.get("client_default")

    return {
        "points_count": len(records),
        "event_date": records[0].get("event_date") if records else None,
        "client": client_display,
        "all_conforme_abnt": all(overall_values) if overall_values else None,
        "all_below_configured_vibration_limit": all(vibration_status_values) if vibration_status_values else None,
        "max_pspl": {
            "value_db": max_pspl_record.get("pspl_db") if max_pspl_record else None,
            "point_name": max_pspl_record.get("point_name") if max_pspl_record else None,
        },
        "max_ppv": {
            "value_mm_s": max_ppv_record.get("evaluation", {}).get("ppv_max_mm_s") if max_ppv_record else None,
            "axis": max_ppv_record.get("evaluation", {}).get("ppv_max_axis") if max_ppv_record else None,
            "point_name": max_ppv_record.get("point_name") if max_ppv_record else None,
        },
        "max_pvs": {
            "value_mm_s": max_pvs_record.get("pvs_mm_s") if max_pvs_record else None,
            "point_name": max_pvs_record.get("point_name") if max_pvs_record else None,
        },
    }
