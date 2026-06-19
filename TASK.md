# TASK

## Contexto
O repositorio possui um hub visual OpenBlast para ferramentas da operação US Vale Verde. A base precisa ser organizada como um sistema de dados auditavel, reutilizavel e compreensivel por terceiros.

## Objetivo
Transformar a planilha de entrada em manifestos validados para dois hubs, com configuracao externa, logs por execucao, saidas reproduziveis, copy revisada e testes minimos.

## Escopo
- Criar arquitetura modular em `src/`.
- Criar configuracao externa em `config.json`.
- Criar documentacao tecnica e operacional.
- Criar validacao de dados antes do processamento.
- Criar saida consumida pelo front-end.
- Criar agrupamento de ferramentas por hub no manifesto e no front-end com copy objetiva.
- Criar publicacao do hub US Vale Verde e publicacao publica filtrada.
- Criar testes automatizados minimos.
- Manter `correcao-de-cargas`, `analisador-de-sismograma`, `openblast-nbr9653` e `analise-de-desvios-de-inclinacao-e-azimute` no hub `Ferramentas Gerais`.

## Fora de escopo
- Reescrever o visual do hub.
- Trocar a planilha por outro formato de origem.
- Implementar banco de dados ou backend persistente.

## Entregaveis
- Documentacao completa.
- `config.json`.
- `main.py`.
- Modulos em `src/`.
- Testes em `tests/`.
- Manifesto US Vale Verde em `output/usvaleverde/`.
- Manifesto publico em `output/public/`.
- Logs em `logs/`.

## Criterios de aceite
- Todos os arquivos obrigatorios existem e nao estao vazios.
- A planilha e lida e validada antes do processamento.
- O manifesto gerado alimenta o front-end.
- A execucao gera log e resumo identificaveis.
- Os testes passam.
