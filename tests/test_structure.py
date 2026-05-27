from __future__ import annotations


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
        "config.json",
        "main.py",
        "requirements.txt",
        "index.html",
        "script.js",
        "styles.css",
        "src/__init__.py",
        "src/config_loader.py",
        "src/data_reader.py",
        "src/exceptions.py",
        "src/logger_setup.py",
        "src/models.py",
        "src/output_writer.py",
        "src/processor.py",
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
    script_text = (project_root / "script.js").read_text(encoding="utf-8")
    assert 'rel="preload" href="output/tools_manifest.json" as="fetch"' in index_text
    assert 'script src="script.js" defer' in index_text
    assert "output/tools_manifest.json" in script_text
    assert "renderManifest" in script_text
    assert "hub-grid" in script_text
    assert "?v=${Date.now()}" not in script_text
    assert 'cache: "no-store"' not in script_text
    assert 'cache: "default"' in script_text


def test_frontend_copy_is_clean(project_root):
    index_text = (project_root / "index.html").read_text(encoding="utf-8")
    script_text = (project_root / "script.js").read_text(encoding="utf-8")

    assert "Hub US MVV" not in index_text
    assert "GitHub Pages" not in index_text
    assert "Caixa de Ferramentas" in index_text
    assert "PAINEL DE ACESSO" in index_text
    assert "Abrir página" in script_text
    assert "Não foi possível" in script_text
