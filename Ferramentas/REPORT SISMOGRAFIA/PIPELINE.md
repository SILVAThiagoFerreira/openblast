# Pipeline De Execução

## 1. Carregamento Da Configuração

- Entrada: `config.json`
- Saída: configuração normalizada em memória
- Validação: presença das seções mínimas e tipos esperados

## 2. Inicialização De Logs

- Entrada: configuração validada
- Saída: arquivo de log em `logs/`
- Validação: o arquivo deve ser criado e receber mensagens da execução

## 3. Leitura Das Entradas

- Entrada: pasta ou arquivo CSV definido em `paths.input_dir` ou `--input`
- Saída: lista de registros estruturados
- Validação: os CSVs precisam existir, ser parseáveis e manter os
  qualificadores instrumentais quando presentes

## 4. Validação Das Entradas

- Entrada: registros lidos
- Saída: registros aprovados para processamento
- Validação: campos obrigatórios, datas, numerais e coerência do lote

## 5. Processamento

- Entrada: registros validados
- Saída: registros avaliados e resumo da campanha
- Validação: consistência entre o número de registros e o resumo

## 6. Validação Dos Resultados

- Entrada: resumo e registros processados
- Saída: confirmação de que o resultado pode ser persistido
- Validação: data do evento, quantidade de pontos e coerência mínima

## 7. Geração Das Saídas

- Entrada: resultados processados e configuração
- Saída: PDF, PNG, nota WhatsApp, JSON consolidado, manifesto e gráficos.
  Para até três pontos, PDF e PNG são uma página A4 com resumo, os dois
  gráficos e os cartões; acima disso, o PDF recebe páginas de continuação.
- Validação: todos os arquivos devem existir, ter tamanho maior que zero,
  abrir corretamente e manter a composição visual em escopo textual, cartões
  horizontais por ponto, marcador circular do cabeçalho e rodapé sem
  sobreposição.

## 8. Geração De Logs

- Entrada: mensagens da execução
- Saída: log final em `logs/`
- Validação: o log deve conter início, progresso e encerramento da execução

## 9. Encerramento

- Entrada: manifesto final
- Saída: retorno de sucesso ou erro explícito
- Validação: código de saída zero em sucesso, diferente de zero em falha

## 10. Pipeline web no navegador

- A página aceita um ou mais `.IDFW.CSV` por seleção ou arraste.
- `pages/js/parser.js` lê os arquivos localmente e `validation.js` rejeita
  registros incompletos antes da conformidade.
- `pages/js/report.js` e `pages/js/charts.js` geram o mesmo contrato visual e
  de nomes da versão Python.
- Os downloads do navegador são PDF, PNG, TXT e ZIP; nenhum CSV sai do
  dispositivo.

## 11. Publicação do GitHub Pages

- `pages/` é a fonte de trabalho do checkout Python.
- O repositório dedicado `SILVAThiagoFerreira/report-sismografia` publica
  `main:/docs` em
  `https://silvathiagoferreira.github.io/report-sismografia/`.
- Antes do push, a cópia de `pages/` deve ser sincronizada com `docs/` e a
  publicação deve ser verificada no navegador.
