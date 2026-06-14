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
9. Gerar a publicacao interna completa.
10. Gerar a publicacao publica filtrada.
11. Validar a consistencia das saidas geradas.
12. Escrever `output/tools_manifest.json`.
13. Escrever `output/public/tools_manifest.json`.
14. Escrever `output/run_summary_<run_id>.json`.
15. Sincronizar `index.html` e `public/index.html` com seus manifestos.
16. Registrar o resultado final no log.
17. Encerrar com codigo de saida apropriado.

## Pontos de decisao
- Se o config estiver invalido, a execucao para antes do pipeline.
- Se a planilha nao existir, a execucao falha na etapa de leitura.
- Se a validacao encontrar erros, o manifesto nao e escrito.
- Se a escrita falhar, a execucao falha e registra a causa no log.
- Se um `repository_id` nao estiver alocado a um hub, a configuracao falha antes do processamento.
- Se o target interno nao usar `index.html` ou `output/tools_manifest.json`, a configuracao falha.
- Se `pages_url` usar um caminho canonico com caixa diferente do `repository_id`, a validacao aceita a correspondencia case-insensitive para o GitHub Pages.

## Saidas por etapa
- Config: estrutura normalizada.
- Leitura: linhas e cabecalhos em formato padronizado.
- Validacao: relatorio com erros e avisos.
- Processamento: manifesto JSON.
- Processamento: manifesto JSON com `hubs` agrupados.
- Escrita: manifesto interno, manifesto publico, summary e log.

## Critério operacional
O pipeline so e considerado concluido quando os dois manifestos existem, o summary existe, o log existe e os dois hubs conseguem carregar seus manifestos.
