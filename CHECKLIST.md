# CHECKLIST

## Estrutura
- [x] `README.md` criado e preenchido.
- [x] `AGENTS.md` criado e preenchido.
- [x] `TASK.md` criado e preenchido.
- [x] `SPEC.md` criado e preenchido.
- [x] `CHECKLIST.md` criado e preenchido.
- [x] `PROMPT.md` criado e preenchido.
- [x] `PIPELINE.md` criado e preenchido.
- [x] `DATA_SCHEMA.md` criado e preenchido.
- [x] `config.json` criado e preenchido.
- [x] `main.py` criado e preenchido.
- [x] `src/` criado com modulos separados.
- [x] `input/` presente com a planilha de origem.
- [x] `output/` presente.
- [x] `logs/` presente.
- [x] `tests/` presente.

## Qualidade
- [x] Nenhum arquivo obrigatorio vazio.
- [x] Nenhuma regra critica implícita fora da documentacao.
- [x] Nenhum caminho ou limite relevante hardcoded fora do config.
- [x] Leitura separada de validacao.
- [x] Validacao separada de processamento.
- [x] Processamento separado de escrita.
- [x] Logs gerados por execucao.
- [x] Saidas reproduziveis e identificaveis.

## Validacao
- [x] Config carregavel.
- [x] Planilha validada antes do processamento.
- [x] Manifesto US Vale Verde gerado com sucesso.
- [x] Manifesto publico gerado com sucesso.
- [x] Summary gerado com sucesso.
- [x] Front-end consumindo o manifesto do hub US Vale Verde.
- [x] Front-end publico consumindo o manifesto filtrado.
- [x] Testes minimos executaveis.

## Evolucao
- [x] Mudancas em schema refletidas em docs e testes.
- [x] Novas ferramentas adicionadas via planilha + `tool_metadata`.
- [x] Mudancas de contrato refletidas no front-end.
- [x] Publicacao US Vale Verde e publica configuradas via `publishing.targets`.
