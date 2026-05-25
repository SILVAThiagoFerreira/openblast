# TASK

## Contexto
O repositorio possui um hub visual para ferramentas da Enaex Brasil com foco na operação US Vale Verde. A base precisa ser organizada como um sistema de dados auditavel, reutilizavel e compreensivel por terceiros.

## Objetivo
Transformar a planilha de entrada em um manifesto validado para o hub, com configuracao externa, logs por execucao, saidas reproduziveis, copy revisada e testes minimos.

## Escopo
- Criar arquitetura modular em `src/`.
- Criar configuracao externa em `config.json`.
- Criar documentacao tecnica e operacional.
- Criar validacao de dados antes do processamento.
- Criar saida consumida pelo front-end.
- Criar testes automatizados minimos.

## Fora de escopo
- Adicionar novas ferramentas nao presentes na planilha.
- Reescrever o visual do hub.
- Trocar a planilha por outro formato de origem.
- Implementar banco de dados ou backend persistente.

## Entregaveis
- Documentacao completa.
- `config.json`.
- `main.py`.
- Modulos em `src/`.
- Testes em `tests/`.
- Manifesto em `output/`.
- Logs em `logs/`.

## Criterios de aceite
- Todos os arquivos obrigatorios existem e nao estao vazios.
- A planilha e lida e validada antes do processamento.
- O manifesto gerado alimenta o front-end.
- A execucao gera log e resumo identificaveis.
- Os testes passam.
