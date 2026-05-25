# DATA_SCHEMA

## 1. Planilha de entrada
Arquivo: `input/repositorios_github_pages.xlsx`

### Aba
- Nome esperado: `Repositorios`
- Tipo: planilha Excel
- Obrigatoriedade: obrigatoria

### Cabecalhos obrigatorios
| Campo | Tipo | Obrigatorio | Significado | Formato permitido | Exemplo valido | Exemplo invalido |
|---|---|---:|---|---|---|---|
| `Repositório` | string | sim | Slug do repositorio | letras minusculas, numeros, `-`, `_`, `.` | `enaex-plano-de-voo` | `Plano de Voo` |
| `Título formal` | string | sim | Nome exibido no card | texto livre nao vazio | `PFR - Plano de Fogo Realizado` | vazio |
| `GitHub` | string | sim | URL do repositorio | `https://github.com/<owner>/<repo>` | `https://github.com/SILVAThiagoFerreira/pfr-enaex` | `http://github.com/...` |
| `Pages` | string | sim | URL da pagina publicada | `https://<owner>.github.io/<repo>/` | `https://silvathiagoferreira.github.io/pfr-enaex/` | `https://example.com/pfr-enaex/` |

### Regras de validacao
- Cabecalhos obrigatorios devem existir.
- Cabecalhos extras sao ignorados.
- Linhas totalmente vazias sao ignoradas.
- Linhas parcialmente vazias sao erro.
- `Repositório` deve bater com o nome do repo nas URLs.

## 2. Configuracao
Arquivo: `config.json`

### Seções obrigatorias
- `project`
- `paths`
- `workbook`
- `validation`
- `artifacts`
- `output`
- `tool_metadata`

### Campos relevantes
| Campo | Tipo | Obrigatorio | Significado |
|---|---|---:|---|
| `paths.input_workbook` | string | sim | Caminho relativo da planilha |
| `paths.output_directory` | string | sim | Pasta de saida |
| `paths.logs_directory` | string | sim | Pasta de logs |
| `artifacts.manifest_filename` | string | sim | Nome fixo do manifesto consumido pelo front-end |
| `artifacts.summary_filename_pattern` | string | sim | Padrão do summary por execucao |
| `artifacts.log_filename_pattern` | string | sim | Padrão do log por execucao |
| `validation.repository_id_pattern` | string | sim | Regex para o slug do repositorio |
| `validation.require_tool_metadata` | boolean | sim | Guardrail do pipeline; deve permanecer `true` |
| `tool_metadata.<repo>.description` | string | sim | Descricao do card |
| `tool_metadata.<repo>.kind` | string | sim | Tipo de icone |
| `tool_metadata.<repo>.accent` | string | sim | Cor principal |
| `tool_metadata.<repo>.accent2` | string | sim | Cor secundaria |

## 3. Manifesto gerado
Arquivo: `output/tools_manifest.json`

### Estrutura top-level
| Campo | Tipo | Obrigatorio | Significado |
|---|---|---:|---|
| `manifest_version` | string | sim | Versao do contrato |
| `project` | objeto | sim | Nome e versao do projeto |
| `generated_at` | string | sim | Timestamp ISO 8601 |
| `run_id` | string | sim | Identificador da execucao |
| `source` | objeto | sim | Metadados da planilha |
| `counts` | objeto | sim | Quantidades processadas |
| `validation` | objeto | sim | Resumo da validacao |
| `generator` | objeto | sim | Informacoes do ambiente |
| `tools` | array | sim | Lista de ferramentas |

### Estrutura de `tools[]`
| Campo | Tipo | Obrigatorio | Significado |
|---|---|---:|---|
| `row_number` | inteiro | sim | Linha de origem na planilha |
| `repository_id` | string | sim | Slug do repositorio |
| `formal_title` | string | sim | Titulo exibido |
| `github_url` | string | sim | Link do repositorio |
| `pages_url` | string | sim | Link da pagina publicada |
| `description` | string | sim | Texto do card |
| `kind` | string | sim | Tipo de icone |
| `accent` | string | sim | Cor principal |
| `accent2` | string | sim | Cor secundaria |
| `github_owner` | string | sim | Owner do GitHub |
| `github_repo_name` | string | sim | Nome do repo |
| `pages_owner` | string | sim | Owner do Pages |
| `pages_repo_name` | string | sim | Nome da pagina |
| `order` | inteiro | sim | Ordem de exibicao |

## 4. Summary de execucao
Arquivo: `output/run_summary_<run_id>.json`

### Campos principais
- `run_id`
- `status`
- `stage`
- `message`
- `paths`
- `source`
- `validation`
- `counts`
- `generator`

## 5. Exemplos

### Valido
```json
{
  "repository_id": "pfr-enaex",
  "formal_title": "PFR - Plano de Fogo Realizado",
  "github_url": "https://github.com/SILVAThiagoFerreira/pfr-enaex",
  "pages_url": "https://silvathiagoferreira.github.io/pfr-enaex/"
}
```

### Invalido
```json
{
  "repository_id": "PFR ENAEX",
  "formal_title": "",
  "github_url": "github.com/SILVAThiagoFerreira/pfr-enaex",
  "pages_url": "https://example.com/pfr-enaex/"
}
```
