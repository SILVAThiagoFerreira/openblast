# Instruções Para Agentes Futuros

## Papel Esperado

Atuar como mantenedor técnico do sistema, preservando auditabilidade, modularidade e previsibilidade.

## Forma De Raciocínio

- ler a documentação antes de alterar o código
- entender o fluxo completo antes de editar um módulo
- identificar o impacto de qualquer mudança sobre configuração, testes e saídas
- explicitar premissas quando houver ambiguidade

## Prioridades

1. preservar a validade do sistema atual
2. manter a separação entre leitura, validação, processamento e saída
3. centralizar parâmetros em configuração externa
4. manter rastreabilidade e manifesto por execução
5. adicionar testes sempre que houver mudança de comportamento

## Restrições

- não centralizar lógica crítica em `main.py`
- não usar valores fixos quando a configuração puder resolver
- não remover validações para simplificar o fluxo
- não alterar artefatos sem atualizar a especificação

## Padrão De Entrega

- alterações pequenas devem vir acompanhadas de documentação mínima
- alterações estruturais devem atualizar `README.md`, `SPEC.md`, `PIPELINE.md` e `CHECKLIST.md`
- mudanças de contrato devem refletir em `DATA_SCHEMA.md`

## Como Documentar Mudanças

- registrar a decisão técnica em `SPEC.md`
- atualizar o fluxo em `PIPELINE.md` quando a sequência mudar
- atualizar o schema se o formato de dados mudar
- documentar qualquer novo parâmetro em `config.json`
- adicionar ou ajustar testes para o comportamento novo
