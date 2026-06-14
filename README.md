# Hub de Ferramentas OpenBlast US MVV

## Propósito
Este projeto transforma a planilha `input/repositorios_github_pages.xlsx` em manifestos validados que alimentam dois hubs visuais da OpenBlast US MVV: o hub interno completo e o hub público filtrado, sem as ferramentas da US Vale Verde.

## Problema que resolve
Os hubs visuais precisam de uma fonte de dados confiavel, auditavel e reproduzivel. A planilha guarda os identificadores e URLs das ferramentas, mas o front-end precisa de um formato normalizado, validado e agrupado por hub. Este projeto faz essa ponte.

## Visão geral da arquitetura
- `input/`: planilha de origem com os repositorios.
- `config.json`: parametros externos, regras de validacao, metadados visuais e agrupamento dos hubs.
- `main.py`: unico ponto de entrada.
- `src/`: leitura, validacao, processamento, logs e saida.
- `output/`: manifestos consumidos pelo front-end e resumo de execucao.
- `logs/`: registros timestampados de cada execucao.
- `index.html`: hub interno completo.
- `public/index.html`: hub público filtrado.
- `script.js`, `styles.css`: interface estatica compartilhada pelos dois hubs.

## Fluxo de uso
1. Ajuste a planilha de entrada se necessario.
2. Ajuste `config.json` para novos parametros ou novos repositorios.
3. Execute `python main.py`.
4. Publique os arquivos gerados em `output/` junto com o front-end.

## Entradas esperadas
- `input/repositorios_github_pages.xlsx`
- `config.json`

## Saidas geradas
- `output/tools_manifest.json`
- `output/public/tools_manifest.json`
- `output/run_summary_<run_id>.json`
- `index.html`
- `public/index.html`
- `logs/pipeline_<run_id>.log`

## Como configurar
- `paths`: caminhos de entrada, saida e logs.
- `artifacts`: nomes dos arquivos gerados.
- `validation`: regras de aceite da planilha e dos URLs.
- `tool_metadata`: descricao, tipo de icone e cores de cada ferramenta.
- `hubs`: agrupamento e ordenacao dos hubs exibidos no front-end.
- `publishing.targets`: define quais grupos entram no hub interno e quais entram no hub público.
- As ferramentas `correcao-de-cargas` e `analisador-de-sismograma` pertencem ao hub `Ferramentas Gerais`.
- As ferramentas `openblast-nbr9653` e `conversor-pdf-seguro` tambem pertencem ao hub `Ferramentas Gerais` e aparecem no hub publico.

## Como executar
```bash
python main.py
```

## GitHub Pages
Depois de publicar o repositório, os dois hubs ficam no mesmo projeto:
- Hub Geral: `https://silvathiagoferreira.github.io/hub-de-ferramentas-us-mvv/`
- Hub de Ferramentas Abertas: `https://silvathiagoferreira.github.io/hub-de-ferramentas-us-mvv/public/`

O arquivo `.nojekyll` na raiz evita processamento do Jekyll e mantém os caminhos estáticos servidos como foram gerados.

## Como validar resultados
- `python -m pytest`
- conferir `output/tools_manifest.json`
- conferir `output/run_summary_<run_id>.json`
- conferir `logs/pipeline_<run_id>.log`

## Como evoluir o projeto
- Adicione novas ferramentas na planilha, em `tool_metadata` e no hub correspondente em `hubs.groups`.
- Se a ferramenta puder ser compartilhada, mantenha-a em `Ferramentas Gerais`; se for interna, mantenha-a em `Ferramentas US Vale Verde`.
- As ferramentas `correcao-de-cargas`, `analisador-de-sismograma`, `openblast-nbr9653` e `conversor-pdf-seguro` ja estao mapeadas para `Ferramentas Gerais`.
- Títulos exibidos vêm da planilha; descrições e metadados visuais vêm de `config.json`.
- Nao altere o contrato do manifesto sem atualizar `script.js`, `DATA_SCHEMA.md` e os testes.
- Toda mudanca de regra deve ser documentada em `SPEC.md`.

## Decisoes tecnicas fixadas
- A planilha e a fonte de verdade para IDs e URLs.
- Metadados visuais vivem no config porque nao existem na planilha.
- O front-end consome `output/tools_manifest.json` para o hub interno e `output/public/tools_manifest.json` para o hub publico.
- O front-end renderiza os grupos `Ferramentas Gerais` e `Ferramentas US Vale Verde` no hub interno e somente `Ferramentas Gerais` no hub publico.
- Erros de validacao interrompem a geracao do manifesto.
- `validation.require_tool_metadata` e um guardrail e deve permanecer `true`.
