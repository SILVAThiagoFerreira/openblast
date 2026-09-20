# Especificação Técnica

## Objetivo Funcional

Processar uma campanha sismográfica a partir de CSVs de sismógrafo, avaliar conformidade técnica, gerar relatório executivo, produzir nota de WhatsApp e registrar os artefatos de execução.

## Regras De Negócio

- Cada execução representa uma campanha.
- Os registros de uma execução devem compartilhar a mesma `event_date`.
- A leitura baseia-se nos CSVs processados pelo parser do projeto.
- O resumo executivo usa os dados consolidados dos registros válidos.
- A conformidade de vibração usa a curva configurada em `limits.nbr9653_curve`.
- O limite executivo de vibração usa `limits.vibration_status_mm_s`.
- O site permite alterar o target executivo de vibração por execução, com valor inicial de `0,8 mm/s`.
- O site permite ocultar a linha “Índices de vibração” do relatório sem remover a avaliação dos dados.
- O texto de WhatsApp deve usar apenas formatação compatível com WhatsApp.
- Qualificadores instrumentais `<` e `>` devem ser preservados nos registros e
  exibidos nas saídas, sem serem convertidos silenciosamente em igualdade.
- Os pontos são apresentados na ordem estável dos arquivos de origem quando
  `processing.record_order` está em `source_order` (padrão). A ordenação por
  distância GPS continua disponível quando configurada explicitamente como
  `gps_distance_ascending`.

## Validações Obrigatórias

- A configuração deve existir e ter as seções mínimas definidas.
- Os campos obrigatórios do registro devem existir antes do processamento.
- Valores numéricos precisam ser finitos e não negativos quando aplicável.
- Datas devem seguir `YYYY-MM-DD`.
- Um lote com múltiplas datas de evento é rejeitado por padrão.
- O resumo processado precisa ser coerente com a quantidade de registros.
- Os artefatos finais precisam existir e ter tamanho maior que zero.
- O PDF precisa ser legível, abrir corretamente e conter os títulos dos dois
  gráficos normativos na primeira página.
- O PNG precisa ser um raster A4 válido e legível.

## Tratamento De Erros

- Erros de configuração geram `ConfigurationError`.
- Erros de validação geram `ValidationError`.
- Erros de geração de artefato geram `OutputError`.
- O `main.py` captura erros do domínio do projeto e encerra com código diferente de zero.
- Erros inesperados também encerram a execução com falha explícita.

## Decisões Técnicas

- JSON foi mantido como formato de configuração por já existir no repositório.
- O diretório padrão de saída é `output/`.
- O diretório de logs é `logs/`.
- Os nomes dos arquivos finais usam o prefixo `ENAEX_NSR` e a data do evento.
- O nome da pasta de execução é derivado de data e hora para rastreabilidade.
- O gráfico de vibração usa eixo Y quebrado quando a faixa dos pontos é muito pequena em relação à curva normativa.
- O PNG do relatório é gerado por rasterização direta da primeira página do PDF, preservando a proporção original.
- Para até três pontos, os dois gráficos normativos ficam lado a lado na mesma
  página A4 do resumo. Campanhas maiores usam páginas de continuação apenas
  para os pontos excedentes.
- A composição da primeira página reserva folga fixa para o rodapé, impedindo que cartões e tabelas finais avancem sobre a assinatura visual.
- O resumo executivo usa o título “Resumo da Campanha Realizada”, escopo
  textual com indicador semântico de vibração, conclusão técnica antes dos
  gráficos e cartões horizontais de pontos monitorados com status à direita.
- O cabeçalho é editorial e leve: logo, metadados, tipografia escura e uma
  regra horizontal; não usa selo circular, faixa cinza ou seta decorativa.

## Identidade Visual do Relatório

Definida em `config.json` e consumida por `src/report.py` e `pages/js/`.
Serve como referência para novas edições visuais — mudanças pontuais são
permitidas desde que preservem a linguagem abaixo.

**Paleta.** Branco `#FFFFFF` domina as superfícies. Cinza Enaex `#38424B`
fica nos títulos e elementos estruturais; vermelho `#E20613` é usado com
contenção no logo, nas réguas e nos acentos; `#D9DEE7` é usado nos contornos
e separadores. O verde `#67C70A` continua reservado à indicação positiva;
badges usam fundos e textos semânticos claros configurados como
`status_*_bg` e `status_*_text`.

**Componentes.**
- **Cards** brancos, quase planos, com contorno fino (`card_border_width`),
  raio discreto (`card_radius`) e sem sombra projetada.
- **Section headers** com regra superior cinza, acento vermelho curto e título
  escuro; o parâmetro `section_header_height` preserva o alinhamento entre
  Python e web sem repetir barras pesadas.
- **Réguas vermelhas** curtas abaixo dos H1 “Resumo da Campanha Realizada” e
  “Pontos Monitorados”.
- **Cards de pontos** com cabeçalho tipográfico escuro, divisor fino, tabelas
  internas claras e status à direita; não há régua vertical que altere a
  largura útil dos dados.
- **Selo de status** ("CONFORME ABNT" / "VERIFICAR" / "DADO AUSENTE") em
  badge semântico claro, com ícone compacto e contraste controlado.
- **Tabelas internas** sem bordas nas células: apenas rótulos em cinza-claro e
  linhas horizontais finas (`#D9DEE7`, 0.35–0.4pt) entre linhas.

**Espaçamentos-chave.** `POINT_CARD_GAP=14`, `POINTS_TITLE_GAP=22`,
`CHART_TO_POINTS_GAP=16`, `CHARTS_TOP_LIMIT=484`. Card do escopo com altura
72 para acomodar as quatro linhas do bloco. Card de conclusão em y=488,
escopo em y=566.

**Proporção dos gráficos.** `charts.figure_height=4.8` define a altura útil
compartilhada entre o PNG Python e o Canvas online sem alterar a largura do
card. `charts.web_figure_width=6.5` e `figure_dpi=220` resultam em 1430×763 px
no Canvas; o PDF e a imagem A4 preservam o mesmo enquadramento. O topo dos
cards fica fixo em y=484 para manter a separação da conclusão técnica.

**Rodapé.** Fundo branco em toda a largura, fio vermelho de 1,5 pt no topo,
texto normativo cinza à esquerda, divisor vertical leve e assinatura escura
“DNA • ENAEX” à direita.

## Limitações Conhecidas

- O parser depende do layout dos CSVs compatíveis com a exportação atual.
- O sistema foi calibrado para a campanha e a estrutura de dados observadas neste projeto.
- Se os campos obrigatórios mudarem na origem, a validação deve ser atualizada.

## Critérios De Sucesso

- relatório, PNG, nota, JSON, manifesto e gráficos são gerados corretamente
- os nomes dos arquivos seguem o padrão configurado
- a execução deixa rastro em log e manifesto
- a validação ocorre antes do processamento
- o sistema permanece modular e extensível

## Contrato da versão online

- A aplicação é estática e roda no navegador; não há upload para servidor.
- A entrada é um ou mais `.IDFW.CSV` da mesma campanha.
- O botão **Carregar exemplo** busca somente os três fixtures demonstrativos
  configurados em `config.json`/`pages/js/config.js`; eles têm o mesmo schema do
  cabeçalho IDFW, mas não representam uma fonte operacional.
- A validação ocorre antes da avaliação de conformidade e rejeita campos
  essenciais ausentes, números inválidos e datas de evento misturadas.
- Os downloads mantêm o prefixo `ENAEX_NSR` e a data consolidada do evento.
