# AGENTS

Estas regras valem para qualquer agente ou desenvolvedor que mexa neste projeto.

## Comportamento esperado
- Leia `README.md`, `SPEC.md`, `TASK.md` e `PIPELINE.md` antes de alterar codigo.
- Trate o projeto como um sistema, nao como um script isolado.
- Preserve rastreabilidade: qualquer alteracao relevante deve ficar documentada.

## Restricoes tecnicas
- `main.py` deve apenas orquestrar.
- Leitura, validacao, processamento, logs e saida devem ficar em modulos diferentes.
- Nao hardcode caminhos, limites ou metadados visuais fora de `config.json`.
- Nao introduza fallback silencioso para dados invalidados.

## Padroes de qualidade
- Valide entrada antes de processar.
- Gere logs em toda execucao relevante.
- Use saidas identificaveis por execucao quando a saida nao for um contrato estavel.
- Mantenha o manifesto do front-end como contrato estavel.

## Regras de modificacao
- Mudou schema? Atualize `DATA_SCHEMA.md`, testes e consumidor do front-end.
- Mudou validacao? Atualize `SPEC.md`, `PIPELINE.md` e os testes.
- Mudou configuracao? Atualize `README.md` e `TASK.md`.

## Proibicoes
- Nao concentrar logica critica em um unico arquivo.
- Nao editar o manifesto gerado manualmente.
- Nao esconder erros de validacao.
- Nao adicionar dependencias sem justificativa documentada.

## Evolucao segura
- Toda nova funcionalidade deve entrar primeiro em configuracao, depois em validacao e so entao em processamento.
- Toda nova saida deve ter formato documentado e teste minimo.
- Toda nova fonte de dados deve ser representada em `DATA_SCHEMA.md`.

## Forma correta de adicionar funcionalidades
1. Atualize a especificacao.
2. Atualize a configuracao.
3. Implemente ou ajuste o modulo responsavel.
4. Adicione testes.
5. Gere as saidas novamente.
6. Verifique o impacto no front-end e no Pages.
