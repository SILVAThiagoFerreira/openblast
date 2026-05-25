# PIPELINE

## Fluxo sequencial
1. Carregar `config.json`.
2. Resolver caminhos relativos a partir da pasta do config.
3. Inicializar logs com `run_id` e timestamp.
4. Ler a planilha de entrada.
5. Extrair cabecalhos e linhas brutas.
6. Validar estrutura, semantica e consistencia dos dados.
7. Processar e enriquecer os registros validados.
8. Validar a consistencia da saida gerada.
9. Escrever `output/tools_manifest.json`.
10. Escrever `output/run_summary_<run_id>.json`.
11. Registrar o resultado final no log.
12. Encerrar com codigo de saida apropriado.

## Pontos de decisao
- Se o config estiver invalido, a execucao para antes do pipeline.
- Se a planilha nao existir, a execucao falha na etapa de leitura.
- Se a validacao encontrar erros, o manifesto nao e escrito.
- Se a escrita falhar, a execucao falha e registra a causa no log.

## Saidas por etapa
- Config: estrutura normalizada.
- Leitura: linhas e cabecalhos em formato padronizado.
- Validacao: relatorio com erros e avisos.
- Processamento: manifesto JSON.
- Escrita: manifesto, summary e log.

## Critério operacional
O pipeline so e considerado concluido quando o manifesto existe, o summary existe, o log existe e o front-end consegue carregar o manifesto.
