# Hub de Ferramentas US MVV

## Propósito
Este projeto transforma a planilha `input/repositorios_github_pages.xlsx` em um manifesto validado que alimenta o hub visual da Enaex Brasil para a operação US Vale Verde.

## Problema que resolve
O hub visual precisa de uma fonte de dados confiavel, auditavel e reproduzivel. A planilha guarda os identificadores e URLs das ferramentas, mas o front-end precisa de um formato normalizado e validado. Este projeto faz essa ponte.

## Visão geral da arquitetura
- `input/`: planilha de origem com os repositorios.
- `config.json`: parametros externos, regras de validacao e metadados visuais.
- `main.py`: unico ponto de entrada.
- `src/`: leitura, validacao, processamento, logs e saida.
- `output/`: manifesto consumido pelo front-end e resumo de execucao.
- `logs/`: registros timestampados de cada execucao.
- `index.html`, `script.js`, `styles.css`: interface estatica do hub.

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
- `output/run_summary_<run_id>.json`
- `logs/pipeline_<run_id>.log`

## Como configurar
- `paths`: caminhos de entrada, saida e logs.
- `artifacts`: nomes dos arquivos gerados.
- `validation`: regras de aceite da planilha e dos URLs.
- `tool_metadata`: descricao, tipo de icone e cores de cada ferramenta.

## Como executar
```bash
python main.py
```

## Como validar resultados
- `python -m pytest`
- conferir `output/tools_manifest.json`
- conferir `output/run_summary_<run_id>.json`
- conferir `logs/pipeline_<run_id>.log`

## Como evoluir o projeto
- Adicione novas ferramentas na planilha e em `tool_metadata`.
- Títulos exibidos vêm da planilha; descrições e metadados visuais vêm de `config.json`.
- Nao altere o contrato do manifesto sem atualizar `script.js`, `DATA_SCHEMA.md` e os testes.
- Toda mudanca de regra deve ser documentada em `SPEC.md`.

## Decisoes tecnicas fixadas
- A planilha e a fonte de verdade para IDs e URLs.
- Metadados visuais vivem no config porque nao existem na planilha.
- O front-end consome `output/tools_manifest.json`.
- Erros de validacao interrompem a geracao do manifesto.
- `validation.require_tool_metadata` e um guardrail e deve permanecer `true`.
