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
- Permitir exclusoes pontuais por publicacao via configuracao, sem mexer na planilha de origem.
- Manter as ferramentas locais `plano-de-fogo-previsto` e `ANALIZADOR DE FUROS - OPITDEV` somente no hub US Vale Verde.
- Manter a ferramenta local `Criador de Aviso de Desmonte` somente no hub US Vale Verde.
- Manter a ferramenta local `Criador de Report de Planejamento de Sismografia` somente no hub US Vale Verde.
- Criar testes automatizados minimos.
- Manter `correcao-de-cargas`, `analisador-de-sismograma` e `analise-de-desvios-de-inclinacao-e-azimute` no hub `Ferramentas Gerais`.
- Retirar `openblast-nbr9653` da planilha de origem, dos metadados e dos manifestos publicados após a remoção da ferramenta da pasta de ferramentas.
- Manter a ferramenta de análise de desvios separada do dashboard operacional de inclinação, azimute e profundidade publicado no Hub de Dashboards.

## Fora de escopo
- Reescrever o visual do hub fora do padrão OpenBlast; refinamentos de hierarquia, busca, filtro e responsividade permanecem no escopo quando preservam o padrão visual.
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
- Cards podem ser ocultados de uma homepage especifica por configuracao, sem remover a ferramenta da origem.
