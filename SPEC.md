# SPEC

## Objetivo tecnico
Construir um pipeline que leia a planilha de repositorios, valide estrutura e semantica, enriqueça os dados com metadados visuais externos e gere manifestos JSON consumidos por dois hubs estaticos: o hub US Vale Verde completo e o hub publico filtrado.

## Regras de negocio
1. A planilha de entrada e a fonte de verdade para `repository_id`, `formal_title`, `github_url` e `pages_url`.
2. `config.json` e a fonte de verdade para descricao, tipo de icone e cores de cada ferramenta.
3. O front-end consome `output/usvaleverde/tools_manifest.json` no hub US Vale Verde e `output/public/tools_manifest.json` no hub publico.
4. A ordem das ferramentas no manifesto segue a ordem das linhas da planilha.
5. Cada ferramenta pertence a exatamente um hub definido em `config.json`.
6. `publishing.targets` define quais grupos vao para cada hub publicado.

## Validacoes obrigatorias
- A planilha deve conter a aba configurada em `config.json`.
- Os cabecalhos obrigatorios devem existir.
- `repository_id` nao pode estar vazio.
- `formal_title` nao pode estar vazio.
- `github_url` e `pages_url` devem ser URLs HTTPS validas.
- O nome do repositorio nas URLs deve bater com `repository_id`; em `pages_url`, a comparacao e case-insensitive para cobrir o caminho canonico do GitHub Pages.
- Cada `repository_id` deve existir em `tool_metadata`.
- Cada `repository_id` deve existir em exatamente um grupo de `hubs.groups`.
- Cor de acento deve ser hex valida.
- IDs duplicados sao erro fatal.
- A publicacao US Vale Verde deve usar `output/usvaleverde/tools_manifest.json` e `usvaleverde/index.html`.
- A publicacao publica deve usar `output/public/tools_manifest.json` e `public/index.html`.

## Comportamento esperado
- Linhas totalmente vazias sao ignoradas.
- Colunas extras na planilha sao ignoradas.
- Erros de validacao impedem a geracao do manifesto.
- O resumo de execucao deve registrar sucesso ou falha.
- Cada execucao gera um log timestampado.
- O manifesto US Vale Verde inclui os dois grupos de hub; o manifesto publico inclui apenas `Ferramentas Gerais`.

## Tratamento de erros
- Erros de configuracao: falha imediata antes do pipeline.
- Erros de leitura: falha antes do processamento.
- Erros de validacao: summary com estado `failed` e detalhes das inconsistencias.
- Erros de escrita: falha imediata com log e summary, quando possivel.

## Decisoes tecnicas
- Formato de configuracao: JSON, para evitar dependencia extra de parser.
- Manifesto estavel para o front-end US Vale Verde: `output/usvaleverde/tools_manifest.json`.
- Manifesto estavel para o front-end publico: `output/public/tools_manifest.json`.
- Summary por execucao: arquivo com `run_id` no nome.
- Logs por execucao: arquivo com `run_id` no nome.
- Metadados visuais externos: configuracao, nao planilha.
- Validacao de cabecalhos por presenca, nao por ordem.
- `validation.require_tool_metadata` e um guardrail fixado em `true`; se for alterado, a configuracao falha.
- `hubs.groups` define os blocos que o front-end renderiza e tambem a ordenacao dos cards.
- `publishing.targets` define o recorte de grupo para o hub US Vale Verde e para o hub publico.

## Limitacoes conhecidas
- Novas ferramentas exigem atualizar a planilha e `tool_metadata`.
- Novas ferramentas exigem atualizar a planilha, `tool_metadata` e o grupo correspondente em `hubs.groups`.
- Ferramentas publicas ficam no grupo `Ferramentas Gerais`; ferramentas do hub US Vale Verde ficam em `Ferramentas US Vale Verde`.
- URLs customizadas fora de `github.com` e `github.io` exigem ajuste de configuracao.
- O front-end depende do manifesto gerado; se o arquivo nao existir, a interface mostra erro de carga.
- A raiz do Pages redireciona para `usvaleverde/`; ela nao e um hub.

## Criterios de sucesso
- `python main.py` gera o manifesto do hub US Vale Verde, o manifesto publico, o resumo e o log sem erro.
- `python -m pytest` passa.
- O hub visual carrega os cards a partir do manifesto.
