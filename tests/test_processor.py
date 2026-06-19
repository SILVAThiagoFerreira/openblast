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

    assert len(records) == 9
    assert manifest["counts"]["valid_rows"] == 9
    assert manifest["counts"]["hub_count"] == 2
    assert manifest["publication"]["slug"] == "usvaleverde"
    assert "tool_count" not in manifest["hubs"][0]
    assert "tool_count" not in manifest["hubs"][1]
    assert [hub["title"] for hub in manifest["hubs"]] == [
        "Ferramentas Gerais",
        "Ferramentas US Vale Verde",
    ]
    assert [tool["formal_title"] for tool in manifest["hubs"][0]["tools"]] == [
        "Conversor DXF para KMZ Operacional",
        "Análise de Cargas - OpitAPP",
        "Blasthole Profile Creator",
        "Report Sismografia Enaex",
        "Analisador de Sismograma - Waveform",
        "OpenBlast NBR 9653",
    ]
    assert [tool["formal_title"] for tool in manifest["hubs"][1]["tools"]] == [
        "Consolidação Plan./Exec. | US Vale Verde",
        "Tempos e Movimentos | Carregamento de Explosivo",
        "PFR | Plano de Fogo Realizado",
    ]
    assert [tool["formal_title"] for tool in manifest["tools"]] == [
        "Conversor DXF para KMZ Operacional",
        "Consolidação Plan./Exec. | US Vale Verde",
        "Tempos e Movimentos | Carregamento de Explosivo",
        "Blasthole Profile Creator",
        "PFR | Plano de Fogo Realizado",
        "Report Sismografia Enaex",
        "Analisador de Sismograma - Waveform",
        "Análise de Cargas - OpitAPP",
        "OpenBlast NBR 9653",
    ]
    assert manifest["tools"][7]["description"] == (
        "Aplicação web para análise de carregamento em operações de perfuração e desmonte, com foco em identificar desvios de profundidade e carga total real em relação ao padrão estatístico do conjunto analisado."
    )
    assert manifest["tools"][1]["description"] == (
        "Algoritmo para consolidação operacional de dados de perfuração planejada e executada | US Vale Verde."
    )
    assert manifest["tools"][2]["description"] == (
        "Sistema de acompanhamento de frota em operações de carregamento de explosivo para análise de tempos e movimentos."
    )
    assert manifest["tools"][4]["description"] == (
        "Algoritmo para consolidação de dados do O-PitSurface, DRB e perfuração do cliente em formato modelável de plano de fogo (*.XLSX)."
    )
    assert manifest["tools"][6]["description"] == (
        "Análise de sismogramas em CSV com gráficos por canal, intervalos de desmonte e exportação de relatório em PDF."
    )


def test_processor_builds_public_manifest(temp_workspace):
    config = load_config(temp_workspace["config_path"])
    workbook = read_workbook(
        temp_workspace["input_workbook"],
        config["workbook"]["sheet_name"],
        config["workbook"]["header_row"],
    )
    records = build_tool_records(config, workbook)
    generated_at = make_timestamp(config)
    public_target = config["resolved_publication_targets"][0]
    manifest = build_manifest(
        config,
        workbook,
        records,
        "20260525_120000",
        generated_at,
        publication_target=public_target,
    )

    assert manifest["publication"]["slug"] == "public"
    assert manifest["counts"]["valid_rows"] == 6
    assert manifest["counts"]["hub_count"] == 1
    assert "tool_count" not in manifest["hubs"][0]
    assert [hub["title"] for hub in manifest["hubs"]] == ["Ferramentas Gerais"]
    assert [tool["formal_title"] for tool in manifest["tools"]] == [
        "Conversor DXF para KMZ Operacional",
        "Blasthole Profile Creator",
        "Report Sismografia Enaex",
        "Analisador de Sismograma - Waveform",
        "Análise de Cargas - OpitAPP",
        "OpenBlast NBR 9653",
    ]
