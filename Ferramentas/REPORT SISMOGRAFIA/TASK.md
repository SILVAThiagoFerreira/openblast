# Tarefa Atual

## Contexto

O projeto já gera relatório sismográfico a partir de CSVs, mas precisava ser
reorganizado como sistema formal e disponibilizado online: configurável,
auditável, validado, compacto e documentado.

## Objetivo

Transformar o repositório em uma base estruturada para produção e evolução,
com separação clara de responsabilidades, rastreabilidade de execução,
artefatos nomeados de forma padronizada e uma versão web funcional no GitHub
Pages.

## Escopo

- estruturar documentação de sistema
- normalizar configuração externa
- separar leitura, validação, processamento e saída em módulos
- registrar logs de execução
- garantir nomes rastreáveis para os artefatos
- adicionar testes mínimos de validação
- publicar o gerador web no repositório Pages dedicado
- reduzir textos e consolidar o PDF/PNG em uma página A4 para até três pontos

## Fora De Escopo

- mudar a lógica técnica de conformidade da campanha
- alterar a interpretação dos CSVs de origem
- adicionar novas fontes de dados

## Ajustes Incorporados

- O PDF/PNG para até três pontos agora concentra resumo, gráficos e pontos em
  uma única página A4, mantendo a legibilidade dos gráficos.
- O layout de referência da campanha de 17/09/2026 foi incorporado: título
  “Resumo da Campanha Realizada”, escopo com a frase completa de fontes
  processadas, conclusão antes dos gráficos, cards sem régua vertical e
  status em pill com ícone.
- A proporção compartilhada dos dois gráficos usa `figure_height=4.4`, card
  de 162 pt e `CHART_TO_POINTS_GAP=28`; o Canvas web gera raster A4 de
  2481×3508 px.
- A ordem padrão dos pontos passou a ser a ordem estável dos arquivos de
  origem, mantendo a distância GPS como opção configurável.
- A nota WhatsApp preserva o texto operacional de referência, os qualificadores
  instrumentais e as quebras de linha Windows.
- O gerador web tem interface compacta, validação explícita, preservação de
  qualificadores `<` e `>` e downloads com o padrão `ENAEX_NSR-YYYYMMDD`.
- A publicação usa `https://silvathiagoferreira.github.io/report-sismografia/`
  e a pasta `docs/` do repositório dedicado.

## Entregáveis

- arquivos de documentação completos
- `config.json` normalizado
- módulos em `src/` com responsabilidades separadas
- testes executáveis com `pytest`
- diretórios operacionais `input/`, `output/`, `logs/`, `tests/`
- versão web em `pages/` e cópia publicada em `docs/`

## Critérios De Aceite

- o projeto executa por um único ponto de entrada
- a configuração é externa
- as entradas são validadas antes do processamento
- os artefatos finais são nomeados de forma identificável
- os logs são gerados por execução
- há testes mínimos cobrindo carregamento, validação, processamento e saída
- o fluxo online gera PDF, PNG, TXT e ZIP sem enviar CSVs para servidor
- os arquivos de entrada e as saídas operacionais permanecem fora do commit
