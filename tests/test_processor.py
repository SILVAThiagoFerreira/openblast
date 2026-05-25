from __future__ import annotations

from src.config_loader import load_config
from src.data_reader import read_workbook
from src.processor import build_manifest, build_tool_records, make_timestamp
from src.validator import validate_inputs


def test_processor_builds_manifest(temp_workspace):
    config = load_config(temp_workspace["config_path"])
    workbook = read_workbook(
        temp_workspace["input_workbook"],
        config["workbook"]["sheet_name"],
        config["workbook"]["header_row"],
    )
    report = validate_inputs(config, workbook)
    assert report.is_valid

    records = build_tool_records(config, workbook)
    generated_at = make_timestamp(config)
    manifest = build_manifest(config, workbook, records, "20260525_120000", generated_at)

    assert len(records) == 6
    assert manifest["counts"]["valid_rows"] == 6
    assert [tool["formal_title"] for tool in manifest["tools"]] == [
        "Conversor DXF para KMZ Operacional",
        "Consolidação Plan./Exec. | US Vale Verde",
        "Tempos e Movimentos | Carregamento de Explosivo",
        "Blasthole Profile Creator",
        "PFR | Plano de Fogo Realizado",
        "Report Sismografia Enaex",
    ]
    assert manifest["tools"][1]["description"] == (
        "Algoritmo para consolidação operacional de dados de perfuração planejada e executada | US Vale Verde."
    )
    assert manifest["tools"][2]["description"] == (
        "Sistema de acompanhamento de frota em operações de carregamento de explosivo para análise de tempos e movimentos."
    )
    assert manifest["tools"][4]["description"] == (
        "Algoritmo para consolidação de dados do O-PitSurface, DRB e perfuração do cliente em formato modelável de plano de fogo (*.XLSX)."
    )
