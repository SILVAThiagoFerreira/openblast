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
    manifest = build_manifest(
        config,
        workbook,
        records,
        "20260525_120000",
        generated_at,
        publication_target=config["resolved_primary_publication_target"],
    )

    assert len(records) == 13
    assert manifest["counts"]["valid_rows"] == 13
    assert manifest["counts"]["hub_count"] == 2
    assert manifest["publication"]["slug"] == "usvaleverde"
    assert "tool_count" not in manifest["hubs"][0]
    assert "tool_count" not in manifest["hubs"][1]
    assert [hub["title"] for hub in manifest["hubs"]] == [
        "Ferramentas Gerais",
        "Ferramentas Locais",
    ]
    assert [tool["formal_title"] for tool in manifest["hubs"][0]["tools"]] == [
            "Conversor: Boreholes/DXF para Limite DXF e e KMZ (Plano de Voo)",
            "Análise de Cargas - OpitAPP",
            "Criador de Perfil de Furo de Desmonte",
            "Report de Monitoramento Sismografico",
            "Analisador de Sismograma - Waveform",
            "ABNT NBR 9653*",
            "Análise de Desvios de Inclinação e Azimute",
        ]
    assert [tool["formal_title"] for tool in manifest["hubs"][1]["tools"]] == [
        "Consolidação Plan./Exec. | US Vale Verde",
        "Tempos e Movimentos | Carregamento de Explosivo",
        "Plano de Fogo Realizado",
        "Plano de Fogo Previsto",
        "ANALIZADOR DE FUROS - OPITDEV",
        "Criador de Aviso de Desmonte",
    ]
    assert [tool["formal_title"] for tool in manifest["tools"]] == [
            "Conversor: Boreholes/DXF para Limite DXF e e KMZ (Plano de Voo)",
                "Consolidação Plan./Exec. | US Vale Verde",
                    "Tempos e Movimentos | Carregamento de Explosivo",
                        "Criador de Perfil de Furo de Desmonte",
                "Plano de Fogo Realizado",
                "Report de Monitoramento Sismografico",
            "Analisador de Sismograma - Waveform",
        "Análise de Cargas - OpitAPP",
        "ABNT NBR 9653*",
        "Análise de Desvios de Inclinação e Azimute",
        "Plano de Fogo Previsto",
        "ANALIZADOR DE FUROS - OPITDEV",
        "Criador de Aviso de Desmonte",
    ]
    assert manifest["tools"][1]["description"] == (
        "Algoritmo para consolidação operacional de dados de perfuração planejada e executada."
    )
    assert manifest["tools"][2]["description"] == (
        "Sistema de acompanhamento de frota em operações de carregamento de explosivo para análise de tempos e movimentos."
    )
    assert manifest["tools"][2]["status"] == "Em desenvolvimento"
    assert manifest["tools"][2]["status_indicator"] is False
    assert manifest["tools"][1]["status"] == "Online"
    assert manifest["tools"][1]["status_indicator"] is True
    assert manifest["tools"][7]["description"] == (
        "Aplicação web para análise de carregamento em operações de perfuração e desmonte, com foco em identificar desvios de profundidade e carga total real em relação ao padrão estatístico do conjunto analisado."
    )
    assert manifest["tools"][9]["description"] == (
        "Dashboard estático para análise de desvios de inclinação, azimute e profundidade a partir de DXF de execução de furos."
    )
    assert manifest["tools"][11]["description"] == (
        "Analisador local de furos a partir de DXF do O-PitDev, com seleção entre pré-corte e face, tratativas por furo e exportação de lâmina operacional em PNG/PDF."
    )
    assert manifest["tools"][12]["description"] == (
        "Criação de avisos de desmonte com áreas de influência, estruturas próximas, croqui operacional e exportação em PDF."
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
    assert manifest["counts"]["valid_rows"] == 7
    assert manifest["counts"]["hub_count"] == 1
    assert "tool_count" not in manifest["hubs"][0]
    assert [hub["title"] for hub in manifest["hubs"]] == ["Ferramentas Gerais"]
    assert [tool["formal_title"] for tool in manifest["tools"]] == [
        "Conversor: Boreholes/DXF para Limite DXF e e KMZ (Plano de Voo)",
            "Criador de Perfil de Furo de Desmonte",
                "Report de Monitoramento Sismografico",
        "Analisador de Sismograma - Waveform",
        "Análise de Cargas - OpitAPP",
        "ABNT NBR 9653*",
        "Análise de Desvios de Inclinação e Azimute",
    ]
