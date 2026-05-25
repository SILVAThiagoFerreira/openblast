# SPEC

## Objetivo tecnico
Construir um pipeline que leia a planilha de repositorios, valide estrutura e semantica, enriqueça os dados com metadados visuais externos e gere um manifesto JSON consumido pelo hub statico.

## Regras de negocio
1. A planilha de entrada e a fonte de verdade para `repository_id`, `formal_title`, `github_url` e `pages_url`.
2. `config.json` e a fonte de verdade para descricao, tipo de icone e cores de cada ferramenta.
3. O front-end consome somente `output/tools_manifest.json`.
4. A ordem das ferramentas no manifesto segue a ordem das linhas da planilha.

## Validacoes obrigatorias
- A planilha deve conter a aba configurada em `config.json`.
- Os cabecalhos obrigatorios devem existir.
- `repository_id` nao pode estar vazio.
- `formal_title` nao pode estar vazio.
- `github_url` e `pages_url` devem ser URLs HTTPS validas.
- O nome do repositorio nas URLs deve bater com `repository_id`.
- Cada `repository_id` deve existir em `tool_metadata`.
- Cor de acento deve ser hex valida.
- IDs duplicados sao erro fatal.

## Comportamento esperado
- Linhas totalmente vazias sao ignoradas.
- Colunas extras na planilha sao ignoradas.
- Erros de validacao impedem a geracao do manifesto.
- O resumo de execucao deve registrar sucesso ou falha.
- Cada execucao gera um log timestampado.

## Tratamento de erros
- Erros de configuracao: falha imediata antes do pipeline.
- Erros de leitura: falha antes do processamento.
- Erros de validacao: summary com estado `failed` e detalhes das inconsistencias.
- Erros de escrita: falha imediata com log e summary, quando possivel.

## Decisoes tecnicas
- Formato de configuracao: JSON, para evitar dependencia extra de parser.
- Manifesto estavel para o front-end: `output/tools_manifest.json`.
- Summary por execucao: arquivo com `run_id` no nome.
- Logs por execucao: arquivo com `run_id` no nome.
- Metadados visuais externos: configuracao, nao planilha.
- Validacao de cabecalhos por presenca, nao por ordem.
- `validation.require_tool_metadata` e um guardrail fixado em `true`; se for alterado, a configuracao falha.

## Limitacoes conhecidas
- Novas ferramentas exigem atualizar a planilha e `tool_metadata`.
- URLs customizadas fora de `github.com` e `github.io` exigem ajuste de configuracao.
- O front-end depende do manifesto gerado; se o arquivo nao existir, a interface mostra erro de carga.

## Criterios de sucesso
- `python main.py` gera manifesto, resumo e log sem erro.
- `python -m pytest` passa.
- O hub visual carrega os cards a partir do manifesto.
