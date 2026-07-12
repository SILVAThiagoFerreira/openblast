# OpenBlast

## Propósito
Este projeto transforma a planilha `input/repositorios_github_pages.xlsx` em manifestos validados que alimentam dois hubs visuais da OpenBlast US MVV: o hub US Vale Verde completo e o hub público filtrado, sem os botões de alternância entre hubs.

## Problema que resolve
Os hubs visuais precisam de uma fonte de dados confiavel, auditavel e reproduzivel. A planilha guarda os identificadores e URLs das ferramentas, mas o front-end precisa de um formato normalizado, validado e agrupado por hub. Este projeto faz essa ponte.

## Visão geral da arquitetura
- `input/`: planilha de origem com os repositorios.
- `config.json`: parametros externos, regras de validacao, metadados visuais e agrupamento dos hubs.
- `main.py`: unico ponto de entrada.
- `src/`: leitura, validacao, processamento, logs e saida.
- `output/`: manifestos consumidos pelo front-end e resumo de execucao.
- `logs/`: registros timestampados de cada execucao.
- `index.html`: redirecionamento para `usvaleverde/`.
- `public/index.html`: hub público filtrado.
- `usvaleverde/index.html`: hub US Vale Verde completo.
- `script.js`, `styles.css`: interface estatica compartilhada pelos dois hubs.
- `VISUAL_STANDARD.md`: contrato do padrao visual OpenBlast para futuras alteracoes de interface.

## Fluxo de uso
1. Ajuste a planilha de entrada se necessario.
2. Ajuste `config.json` para novos parametros ou novos repositorios.
3. Execute `python main.py`.
4. Publique os arquivos gerados em `output/` junto com o front-end.

## Entradas esperadas
- `input/repositorios_github_pages.xlsx`
- `config.json`

## Saidas geradas
- `output/usvaleverde/tools_manifest.json`
- `output/public/tools_manifest.json`
- `output/run_summary_<run_id>.json`
- `index.html`
- `public/index.html`
- `usvaleverde/index.html`
- `logs/pipeline_<run_id>.log`

## Como configurar
- `paths`: caminhos de entrada, saida e logs.
- `artifacts`: nomes dos arquivos gerados.
- `validation`: regras de aceite da planilha e dos URLs.
- `tool_metadata`: descricao, tipo de icone e cores de cada ferramenta.
- `hubs`: agrupamento, ordenacao e copy dos hubs exibidos no front-end.
- `publishing.targets`: define quais grupos entram no hub US Vale Verde e quais entram no hub público.
- `publishing.targets[].excluded_repository_ids`: remove cards específicos de uma publicação sem alterar a planilha; use quando a ferramenta continua existindo na origem, mas nao deve aparecer em uma homepage publica.
- As ferramentas `correcao-de-cargas` e `analisador-de-sismograma` pertencem ao hub `Ferramentas Gerais`.
- A ferramenta `openblast-nbr9653` tambem pertence ao hub `Ferramentas Gerais` e aparece no hub publico.
- A ferramenta `analise-de-desvios-de-inclinacao-e-azimute` tambem pertence ao hub `Ferramentas Gerais` e aparece nos dois hubs de ferramentas.
- As ferramentas `usmvv_planned_and_executed_data_consolidation`, `temposemovimentos` e `pfr-openblast` pertencem ao hub `Ferramentas US Vale Verde`; `temposemovimentos` é excluída da publicação deste hub porque foi transferida para o hub de dashboards.

## Como executar
```bash
python main.py
```

## GitHub Pages
Depois de publicar o repositório, os dois hubs ficam no mesmo projeto:
- Raiz do projeto: `https://silvathiagoferreira.github.io/openblast/` redireciona para `usvaleverde/`
- Hub US Vale Verde: `https://silvathiagoferreira.github.io/openblast/usvaleverde/`
- Hub de Ferramentas Abertas: `https://silvathiagoferreira.github.io/openblast/public/`

O arquivo `.nojekyll` na raiz evita processamento do Jekyll e mantém os caminhos estáticos servidos como foram gerados.

## Como validar resultados
- `python -m pytest`
- conferir `output/usvaleverde/tools_manifest.json`
- conferir `output/run_summary_<run_id>.json`
- conferir `logs/pipeline_<run_id>.log`

## Padrao visual
Mudancas de interface devem seguir `VISUAL_STANDARD.md`. Esse arquivo descreve o padrao OpenBlast de luxo discreto, tons de branco, geometria mais quadrada, presenca minima do logo e regras para futuras IAs ou desenvolvedores.

## Como evoluir o projeto
- Adicione novas ferramentas na planilha, em `tool_metadata` e no hub correspondente em `hubs.groups`.
- Se a ferramenta puder ser compartilhada, mantenha-a em `Ferramentas Gerais`; se for interna, mantenha-a em `Ferramentas US Vale Verde`.
- As ferramentas `correcao-de-cargas`, `analisador-de-sismograma`, `openblast-nbr9653` e `analise-de-desvios-de-inclinacao-e-azimute` ja estao mapeadas para `Ferramentas Gerais`.
- Se uma ferramenta precisar sair de apenas uma publicacao, prefira `publishing.targets[].excluded_repository_ids` em vez de remover a linha da planilha.
- Títulos exibidos vêm da planilha; descrições e metadados visuais vêm de `config.json`.
- Nao altere o contrato do manifesto sem atualizar `script.js`, `DATA_SCHEMA.md` e os testes.
- Toda mudanca de regra deve ser documentada em `SPEC.md`.

## Decisoes tecnicas fixadas
- A planilha e a fonte de verdade para IDs e URLs.
- Metadados visuais vivem no config porque nao existem na planilha.
- O front-end consome `output/usvaleverde/tools_manifest.json` para o hub US Vale Verde e `output/public/tools_manifest.json` para o hub publico.
- O front-end renderiza os grupos `Ferramentas Gerais` e `Ferramentas US Vale Verde` no hub US Vale Verde e somente `Ferramentas Gerais` no hub publico.
- Erros de validacao interrompem a geracao do manifesto.
- `validation.require_tool_metadata` e um guardrail e deve permanecer `true`.
