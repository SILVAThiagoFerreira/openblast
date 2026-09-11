from __future__ import annotations

import re

def test_required_files_exist_and_are_not_empty(project_root):
    required_files = [
        "README.md",
        "AGENTS.md",
        "TASK.md",
        "SPEC.md",
        "CHECKLIST.md",
        "PROMPT.md",
        "PIPELINE.md",
        "DATA_SCHEMA.md",
        "VISUAL_STANDARD.md",
        "config.json",
        "main.py",
        "requirements.txt",
        "index.html",
        "script.js",
        "styles.css",
        "public/index.html",
        "usvaleverde/index.html",
        "src/__init__.py",
        "src/config_loader.py",
        "src/data_reader.py",
        "src/exceptions.py",
        "src/logger_setup.py",
        "src/models.py",
        "src/output_writer.py",
        "src/processor.py",
        "src/frontend_sync.py",
        "src/validator.py",
    ]

    for relative_path in required_files:
        path = project_root / relative_path
        assert path.exists(), f"Missing file: {relative_path}"
        assert path.stat().st_size > 0, f"Empty file: {relative_path}"


def test_runtime_directories_exist(project_root):
    for relative_path in ["input", "output", "logs", "tests", "src"]:
        assert (project_root / relative_path).exists(), f"Missing directory: {relative_path}"


def test_frontend_reads_generated_manifest(project_root):
    index_text = (project_root / "index.html").read_text(encoding="utf-8")
    public_index_text = (project_root / "public" / "index.html").read_text(encoding="utf-8")
    us_index_text = (project_root / "usvaleverde" / "index.html").read_text(encoding="utf-8")
    script_text = (project_root / "script.js").read_text(encoding="utf-8")
    assert 'meta http-equiv="refresh" content="0; url=usvaleverde/"' in index_text
    assert "window.location.replace(\"usvaleverde/\")" in index_text
    assert "<!-- MANIFEST:START -->" not in index_text
    assert '<script type="application/json" id="initial-manifest">' not in index_text
    assert re.search(r'script src="../script\.js\?v=\d{8}_\d{6}" defer data-manifest-url="../output/public/tools_manifest.json"', public_index_text)
    assert re.search(r'link rel="stylesheet" href="../styles\.css\?v=\d{8}_\d{6}"', public_index_text)
    assert "<!-- MANIFEST:START -->" in public_index_text
    assert '<script type="application/json" id="initial-manifest">' in public_index_text
    assert re.search(r'script src="../script\.js\?v=\d{8}_\d{6}" defer data-manifest-url="../output/usvaleverde/tools_manifest.json"', us_index_text)
    assert "<!-- MANIFEST:START -->" in us_index_text
    assert '<script type="application/json" id="initial-manifest">' in us_index_text
    assert "output/public/tools_manifest.json" in script_text
    assert "output/usvaleverde/tools_manifest.json" in script_text
    assert "output/tools_manifest.json" not in script_text
    assert "renderManifest" in script_text
    assert "hub-grid" in script_text
    assert 'cache: "no-store"' not in script_text
    assert 'cache: "default"' in script_text
    assert "initial-manifest" in script_text
    assert "hub-section__count" not in (project_root / "styles.css").read_text(encoding="utf-8")


def test_frontend_copy_is_clean(project_root):
    index_text = (project_root / "index.html").read_text(encoding="utf-8")
    public_index_text = (project_root / "public" / "index.html").read_text(encoding="utf-8")
    us_index_text = (project_root / "usvaleverde" / "index.html").read_text(encoding="utf-8")
    script_text = (project_root / "script.js").read_text(encoding="utf-8")
    config_text = (project_root / "config.json").read_text(encoding="utf-8")

    assert "OpenBlast" in index_text
    assert "usvaleverde/" in index_text
    assert "meta http-equiv=\"refresh\"" in index_text
    assert "<!-- MANIFEST:START -->" not in index_text
    assert "topbar__nav" not in public_index_text
    assert "topbar__nav" not in us_index_text
    assert "Hub Geral" not in public_index_text
    assert "Hub Aberto" not in public_index_text
    assert "Hub Geral" not in us_index_text
    assert "Hub Aberto" not in us_index_text
    assert "Ferramentas" in public_index_text
    assert "Ferramentas" in us_index_text
    assert "Selecione um hub para abrir a ferramenta desejada." not in public_index_text
    assert "Selecione um hub para abrir a ferramenta desejada." not in us_index_text
    assert "Ferramentas corporativas e operacionais de uso transversal." not in config_text
    assert "Ferramentas corporativas e operacionais de uso transversal." not in public_index_text
    assert "Ferramentas corporativas e operacionais de uso transversal." not in us_index_text
    assert "VISUAL/LOGO%20OPENBLAST%20TRANSPARENTE.png" in public_index_text
    assert "VISUAL/LOGO%20OPENBLAST%20TRANSPARENTE.png" in us_index_text
    assert "brand__wordmark" in public_index_text
    assert "brand__wordmark" in us_index_text
    assert public_index_text.count("brand__logo") == 1
    assert us_index_text.count("brand__logo") == 1
    assert "hero__title-row" not in public_index_text
    assert "hero__title-row" not in us_index_text
    assert "tool-card__hex" in script_text
    assert "tool-card__link" not in script_text
    assert "Acesso rápido" not in public_index_text
    assert "Acesso rápido" not in us_index_text
    assert "Hubs disponíveis" not in public_index_text
    assert "Hubs disponíveis" not in us_index_text
    assert "Acesso direto ao conjunto de ferramentas operacionais da unidade." not in us_index_text
    assert "Ferramentas operacionais da OpenBlast." not in us_index_text
    assert "hero__description" not in public_index_text
    assert "hero__description" not in us_index_text
    assert "<span>Ferramentas</span>" not in public_index_text
    assert "<span>Ferramentas</span>" not in us_index_text
    assert "hub-section__count" not in script_text
    assert "7 ferramentas" not in script_text
    assert 'aria-label="Abrir ' in script_text
    assert "directory-controls" in script_text
    assert "directory-count" in script_text
    assert "truncateDescription" in script_text
    assert "maxLength = 100" in script_text
    assert ".directory-controls" in (project_root / "styles.css").read_text(encoding="utf-8")
    assert "--gray-enaex: #38424B" in (project_root / "styles.css").read_text(encoding="utf-8")
    assert "--red-enaex: #E20613" in (project_root / "styles.css").read_text(encoding="utf-8")
    assert "Não foi possível" in script_text
    assert "animation-delay" not in (project_root / "styles.css").read_text(encoding="utf-8")
