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

## Validações Obrigatórias

- A configuração deve existir e ter as seções mínimas definidas.
- Os campos obrigatórios do registro devem existir antes do processamento.
- Valores numéricos precisam ser finitos e não negativos quando aplicável.
- Datas devem seguir `YYYY-MM-DD`.
- Um lote com múltiplas datas de evento é rejeitado por padrão.
- O resumo processado precisa ser coerente com a quantidade de registros.
- Os artefatos finais precisam existir e ter tamanho maior que zero.

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
- Os gráficos normativos ficam em uma segunda página do PDF, cada um em largura total, para garantir legibilidade em impressão e na visualização do documento.
- A composição da primeira página reserva folga fixa para o rodapé, impedindo que cartões e tabelas finais avancem sobre a assinatura visual.
- O resumo executivo usa escopo textual, cabeçalhos verdes e cartões horizontais de pontos monitorados com status à direita.
- O canto superior direito do cabeçalho usa um marcador circular geométrico simples com o número de pontos monitorados dentro.

## Identidade Visual do Relatório

Definida em `src/report.py`. Serve como referência para novas edições visuais — mudanças pontuais são permitidas desde que preservem a linguagem abaixo.

**Paleta.** Verde institucional `#67C70A` para headers de seção, réguas de destaque e status conforme. Vermelho `#E30613` reservado ao logotipo e ao título principal. Cinza escuro `#3C4656` (dark) nos cabeçalhos dos cards de pontos; navy `#151B36` no badge do rodapé. Verde-claro `#EAF6D9` como fundo de rótulos em tabelas. Cinza `#E8EAEE` na faixa superior do card de cabeçalho e `#D9DEE7` nas linhas separadoras.

**Componentes.**
- **Cards** com cantos arredondados (raio 5) e sombra sutil (`#E1E5EA`).
- **Section headers** em barra verde (altura 20) com título branco em Helvetica-Bold.
- **Réguas verdes** curtas (42×2) abaixo dos H1 "Resumo Executivo" e "Pontos Monitorados", unificando a linguagem com os headers das seções.
- **Cards de pontos** com faixa dark no topo e régua verde vertical de 3.5px à esquerda do nome do ponto.
- **Selo de status** ("CONFORME ABNT" / "VERIFICAR" / "DADO AUSENTE") em pill (raio 9), fundo colorido conforme o estado.
- **Tabelas internas** sem bordas nas células: apenas a faixa de rótulo em verde-claro e linhas horizontais finas (`#D9DEE7`, 0.35–0.4pt) entre linhas.

**Espaçamentos-chave.** `POINT_CARD_GAP=14`, `POINTS_TITLE_GAP=22`, `CHART_TO_POINTS_GAP=40`, `CHARTS_TOP_LIMIT=480`. Card do escopo com altura 72 para acomodar as 4 linhas do bloco. Card de conclusão em y=488, escopo em y=566.

**Rodapé.** Texto normativo em cinza `#667085` alinhado verticalmente ao centro do badge navy "DNA • ENAEX". Fio vermelho de 6pt na base da página como assinatura visual.

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
