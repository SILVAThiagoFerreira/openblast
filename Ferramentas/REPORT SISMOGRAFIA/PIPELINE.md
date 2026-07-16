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
- Validação: os CSVs precisam existir e ser parseáveis

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
- Saída: PDF (resumo na primeira página e gráficos normativos em página dedicada), PNG da primeira página, nota WhatsApp, JSON consolidado, manifesto e gráficos
- Validação: todos os arquivos devem existir, ter tamanho maior que zero e manter a composição visual em escopo textual, cartões horizontais por ponto e marcador circular do cabeçalho, sem sobreposição entre conteúdo técnico e rodapé

## 8. Geração De Logs

- Entrada: mensagens da execução
- Saída: log final em `logs/`
- Validação: o log deve conter início, progresso e encerramento da execução

## 9. Encerramento

- Entrada: manifesto final
- Saída: retorno de sucesso ou erro explícito
- Validação: código de saída zero em sucesso, diferente de zero em falha

## 10. Publicação do gerador web

- O workflow de Pages copia `pages/` para a raiz publicada.
- `pages/js/report.js` mantém paridade de coordenadas com `src/report.py`.
- A publicação não deve apontar para `docs/`, pois esse diretório contém o
  dashboard analítico legado e gera uma interface diferente do relatório
  executivo solicitado.
