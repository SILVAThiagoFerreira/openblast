# CHECKLIST

## Estrutura
- [ ] `README.md` criado e preenchido.
- [ ] `AGENTS.md` criado e preenchido.
- [ ] `TASK.md` criado e preenchido.
- [ ] `SPEC.md` criado e preenchido.
- [ ] `CHECKLIST.md` criado e preenchido.
- [ ] `PROMPT.md` criado e preenchido.
- [ ] `PIPELINE.md` criado e preenchido.
- [ ] `DATA_SCHEMA.md` criado e preenchido.
- [ ] `config.json` criado e preenchido.
- [ ] `main.py` criado e preenchido.
- [ ] `src/` criado com modulos separados.
- [ ] `input/` presente com a planilha de origem.
- [ ] `output/` presente.
- [ ] `logs/` presente.
- [ ] `tests/` presente.

## Qualidade
- [ ] Nenhum arquivo obrigatorio vazio.
- [ ] Nenhuma regra critica implícita fora da documentacao.
- [ ] Nenhum caminho ou limite relevante hardcoded fora do config.
- [ ] Leitura separada de validacao.
- [ ] Validacao separada de processamento.
- [ ] Processamento separado de escrita.
- [ ] Logs gerados por execucao.
- [ ] Saidas reproduziveis e identificaveis.

## Validacao
- [ ] Config carregavel.
- [ ] Planilha validada antes do processamento.
- [ ] Manifesto gerado com sucesso.
- [ ] Summary gerado com sucesso.
- [ ] Front-end consumindo o manifesto.
- [ ] Testes minimos executaveis.

## Evolucao
- [ ] Mudancas em schema refletidas em docs e testes.
- [ ] Novas ferramentas adicionadas via planilha + `tool_metadata`.
- [ ] Mudancas de contrato refletidas no front-end.
