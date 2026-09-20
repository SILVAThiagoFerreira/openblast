from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_web_examples_are_configured_and_use_the_idfw_header_contract():
    config = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    examples = config["examples"]

    assert examples["label"] == "Carregar exemplo"
    assert len(examples["files"]) == 3
    for relative_path in examples["files"]:
        fixture = ROOT / "pages" / relative_path
        text = fixture.read_text(encoding="utf-8")
        assert fixture.is_file()
        assert fixture.stat().st_size > 0
        assert '"EventDate","2026-09-17"' in text
        assert '"Tran","Vert","Long","MicL"' in text


def test_web_ui_exposes_the_example_loader_and_pipeline_hook():
    index = (ROOT / "pages" / "index.html").read_text(encoding="utf-8")
    app = (ROOT / "pages" / "js" / "app.js").read_text(encoding="utf-8")

    assert 'id="example-btn"' in index
    assert "const loadExample" in app
    assert "SISMO_CONFIG?.examples" in app
    assert "Exemplo carregado" in app
