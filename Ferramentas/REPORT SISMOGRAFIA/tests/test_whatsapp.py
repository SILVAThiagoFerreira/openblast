from __future__ import annotations

from src.whatsapp import build_whatsapp_note


def test_whatsapp_note_keeps_reference_operational_layout_and_ppv_details():
    config = {
        "project": {
            "client_default": "US MINERAÇÃO VALE-VERDE",
            "base_normativa": "ABNT NBR 9653:2018",
        },
        "limits": {"vibration_status_mm_s": 0.8},
    }
    record = {
        "point_name": "BARRAGEM DE REJEITOS",
        "event_date": "2026-09-17",
        "pvs_mm_s": 0.110,
        "pspl_db": 102.9,
        "tran_ppv_mm_s": 0.127,
        "vert_ppv_mm_s": 0.127,
        "long_ppv_mm_s": 0.127,
        "numeric_qualifiers": {
            "tran_ppv_mm_s": "<",
            "vert_ppv_mm_s": "<",
            "long_ppv_mm_s": "<",
        },
        "evaluation": {"vibration_status_ok": True},
    }
    summary = {
        "event_date": "2026-09-17",
        "client": "US MINERAÇÃO VALE-VERDE",
        "all_below_configured_vibration_limit": True,
    }

    note = build_whatsapp_note([record], summary, config)

    assert "*MONITORAMENTO SISMOGRÁFICO - ENAEX*" in note
    assert "Prezados," in note
    assert "• PPV: Tran <0,127 | Vert <0,127 | Long <0,127 mm/s" in note
    assert "_Consulte a imagem anexa para mais detalhes._" in note
