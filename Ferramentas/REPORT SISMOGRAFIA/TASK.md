# Tarefa Atual

## Contexto

O projeto já gera relatório sismográfico a partir de CSVs, mas precisava ser reorganizado como sistema formal: configurável, auditável, validado e documentado.

## Objetivo

Transformar o repositório em uma base estruturada para produção e evolução, com separação clara de responsabilidades, rastreabilidade de execução e artefatos nomeados de forma padronizada.

## Escopo

- estruturar documentação de sistema
- normalizar configuração externa
- separar leitura, validação, processamento e saída em módulos
- registrar logs de execução
- garantir nomes rastreáveis para os artefatos
- adicionar testes mínimos de validação

## Fora De Escopo

- mudar a lógica técnica de conformidade da campanha
- alterar a interpretação dos CSVs de origem
- criar interface gráfica
- adicionar novas fontes de dados

## Ajuste Visual Incorporado

- Os gráficos normativos deixaram de ser comprimidos em dois cartões lado a lado na primeira página.
- O PDF agora apresenta uma página dedicada, com um gráfico por cartão de largura total; a geração Python e a versão do GitHub Pages mantêm o mesmo layout e configuração.

## Entregáveis

- arquivos de documentação completos
- `config.json` normalizado
- módulos em `src/` com responsabilidades separadas
- testes executáveis com `pytest`
- diretórios operacionais `input/`, `output/`, `logs/`, `tests/`

## Critérios De Aceite

- o projeto executa por um único ponto de entrada
- a configuração é externa
- as entradas são validadas antes do processamento
- os artefatos finais são nomeados de forma identificável
- os logs são gerados por execução
- há testes mínimos cobrindo carregamento, validação, processamento e saída
