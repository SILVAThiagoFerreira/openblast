# Regras Permanentes Do Projeto

Este arquivo define o comportamento esperado de qualquer agente, desenvolvedor ou mantenedor que altere este repositório.

## Princípios

- Tratar o projeto como um sistema auditável, não como um script isolado.
- Manter o `main.py` apenas como ponto de entrada e orquestração.
- Preservar separação entre leitura, validação, processamento, logs e saída.
- Externalizar parâmetros ajustáveis em `config.json`.
- Documentar toda decisão técnica relevante no próprio repositório.

## Regras De Modificação

- Toda alteração funcional deve vir acompanhada de atualização de documentação e teste mínimo.
- Nenhuma regra de negócio deve ficar implícita em strings soltas no código.
- Nomes de arquivos, caminhos, limites e templates de saída não devem ser fixados em lógica interna quando puderem estar na configuração.
- Novas fontes de dados devem entrar por módulo próprio em `src/`.
- Novos formatos de saída devem ser implementados sem quebrar o fluxo existente.

## Validação Obrigatória

- Nenhuma entrada pode seguir para processamento sem validação.
- Configuração inválida deve interromper a execução com erro explícito.
- Resultados processados devem ser validados antes da escrita final.
- Todo artefato gerado deve ser verificado quanto a existência e tamanho.

## Proibições

- Não concentrar lógica crítica em `main.py`.
- Não editar CSVs de entrada.
- Não introduzir valores de limite ou caminhos diretamente no processamento quando a configuração permitir parametrização.
- Não assumir formatos de dados sem registrar a premissa em `SPEC.md`.
- Não remover rastreabilidade, log ou manifesto para simplificar a implementação.

## Evolução Segura

- Primeiro ajustar a especificação, depois o código.
- Se um novo comportamento alterar saídas, atualizar `README.md`, `SPEC.md`, `PIPELINE.md` e os testes.
- Se uma nova premissa for introduzida, registrá-la em `TASK.md` ou `SPEC.md`.
- Preferir compatibilidade retroativa quando possível; quando não for possível, documentar a quebra.
