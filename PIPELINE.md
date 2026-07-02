# PIPELINE

## Fluxo sequencial
1. Carregar `config.json`.
2. Resolver caminhos relativos a partir da pasta do config.
3. Inicializar logs com `run_id` e timestamp.
4. Ler a planilha de entrada.
5. Extrair cabecalhos e linhas brutas.
6. Validar estrutura, semantica e consistencia dos dados.
7. Processar e enriquecer os registros validados.
8. Agrupar os registros por hub conforme `config.json`.
9. Aplicar `publishing.targets[].excluded_repository_ids` ao target de publicacao correspondente.
10. Gerar a publicacao do hub US Vale Verde.
11. Gerar a publicacao publica filtrada.
12. Validar a consistencia das saidas geradas.
13. Escrever `output/usvaleverde/tools_manifest.json`.
14. Escrever `output/public/tools_manifest.json`.
15. Escrever `output/run_summary_<run_id>.json`.
16. Sincronizar `usvaleverde/index.html` e `public/index.html` com seus manifestos.
17. Registrar o resultado final no log.
18. Encerrar com codigo de saida apropriado.

## Pontos de decisao
- Se o config estiver invalido, a execucao para antes do pipeline.
- Se a planilha nao existir, a execucao falha na etapa de leitura.
- Se a validacao encontrar erros, o manifesto nao e escrito.
- Se a escrita falhar, a execucao falha e registra a causa no log.
- Se um `repository_id` nao estiver alocado a um hub, a configuracao falha antes do processamento.
- Se `excluded_repository_ids` tiver um ID desconhecido ou repetido, a configuracao falha antes do processamento.
- Se os targets `public` ou `usvaleverde` nao usarem seus caminhos configurados, a configuracao falha.
- Se `pages_url` usar um caminho canonico com caixa diferente do `repository_id`, a validacao aceita a correspondencia case-insensitive para o GitHub Pages.

## Saidas por etapa
- Config: estrutura normalizada.
- Leitura: linhas e cabecalhos em formato padronizado.
- Validacao: relatorio com erros e avisos.
- Processamento: manifesto JSON.
- Processamento: manifesto JSON com `hubs` agrupados.
- Processamento: manifesto JSON com cards removidos apenas no target configurado.
- Escrita: manifesto US Vale Verde, manifesto publico, summary e log.

## Critério operacional
O pipeline so e considerado concluido quando os dois manifestos existem, o summary existe, o log existe e os dois hubs conseguem carregar seus manifestos.
