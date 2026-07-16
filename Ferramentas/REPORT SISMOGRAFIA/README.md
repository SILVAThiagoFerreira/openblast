# Sistema de Relatório Sismográfico Enaex

Este projeto gera um relatório onepage de monitoramento sismográfico a partir de arquivos CSV exportados pelos sismógrafos compatíveis com o fluxo atual da Enaex.

## Propósito

Resolver a consolidação manual de campanhas sismográficas, produzindo um pacote auditável com relatório PDF, imagem de visualização, nota para WhatsApp, JSON consolidado, gráficos técnicos e log de execução.

## Problema que o sistema resolve

Antes desta estrutura, os dados vinham dos CSVs, mas a transformação para relatório, imagem e mensagem operacional dependia de decisões dispersas no código. O sistema agora centraliza:

- leitura dos CSVs
- validação estrutural e semântica
- processamento técnico
- geração de saídas nomeadas e rastreáveis
- registro de log para auditoria

## Visão geral da arquitetura

O projeto foi organizado em camadas:

- `src/config_loader.py`: carrega e normaliza a configuração externa
- `src/logger_setup.py`: inicializa o log da execução
- `src/data_reader.py`: lê os CSVs e produz registros estruturados
- `src/validator.py`: valida configuração, entradas e resultados processados
- `src/processor.py`: calcula conformidade e resumo da campanha
- `src/output_writer.py`: gera arquivos finais, copia entradas e monta o manifesto
- `src/charts.py`, `src/report.py`, `src/whatsapp.py`: produzem os artefatos de saída

O `main.py` apenas orquestra a sequência.

## Fluxo de uso

1. A configuração é carregada de `config.json`.
2. O logger é preparado em `logs/`.
3. Os CSVs são lidos da pasta `input/` ou do caminho informado por `--input`.
4. As entradas são validadas antes do processamento.
5. O processamento técnico gera resumo e conformidade.
6. Os artefatos são escritos em uma pasta de execução dentro de `output/`.
7. O manifesto aponta para todos os arquivos gerados.

## Entradas esperadas

- CSVs de sismógrafo compatíveis com o parser atual
- Um arquivo de configuração JSON em `config.json`
- Opcionalmente, outro diretório/arquivo informado em `--input`

## Saídas geradas

Cada execução cria uma pasta com data e hora em `output/`, por exemplo:

`output/20260610_144614_monitoramento_sismografico/`

Dentro dela são gerados:

- `ENAEX_NSR-YYYYMMDD.pdf`
- `ENAEX_NSR-YYYYMMDD.png`
- `ENAEX_NSR-YYYYMMDD_nota_whatsapp.txt`
- `ENAEX_NSR-YYYYMMDD_dados_extraidos.json`
- `ENAEX_NSR-YYYYMMDD_manifest.json`
- pasta `graficos/` com os PNGs dos gráficos
- pasta `entrada_csv/` com cópia dos CSVs processados

O relatório usa a primeira página para resumo executivo e pontos monitorados. Os gráficos normativos são apresentados em uma segunda página, em cartões de largura total, para preservar a leitura de eixos, legenda, curva ABNT e anotações.

O escopo é apresentado em linhas textuais, e os pontos monitorados usam cartões horizontais com botão de status à direita.

O cabeçalho usa um marcador circular geométrico simples no canto superior direito.

Os logs ficam em `logs/`.

## Configuração

O arquivo `config.json` centraliza:

- caminhos de entrada, saída e logs
- nomes e templates dos artefatos
- limites técnicos
- parâmetros de gráficos
- target executivo de vibração e visibilidade da linha “Índices de vibração”
- regras de execução

Se um valor precisar mudar, a decisão deve ser feita na configuração, não no código.

## Como executar

Instalação:

```bash
pip install -r requirements.txt
```

Execução com a pasta padrão:

```bash
python main.py --config config.json
```

Execução com outra entrada:

```bash
python main.py --input examples/input --config config.json
```

Execução com outra raiz de saída:

```bash
python main.py --input examples/input --config config.json --out output
```

## Como validar resultados

1. Confirme que a pasta de execução foi criada em `output/`.
2. Abra o `manifest` e verifique os caminhos dos artefatos.
3. Confirme que o log foi criado em `logs/`.
4. Verifique se o PDF, PNG, nota e JSON existem e têm tamanho maior que zero.
5. Rode os testes automatizados com `pytest`.

## Publicação web

O GitHub Pages publica exclusivamente a pasta `pages/`. Ela contém o
gerador onepage no navegador e usa o mesmo layout A4 do relatório Python:
identidade ENAEX, resumo executivo, gráficos NBR 9653:2018, cartões de pontos
monitorados e rodapé institucional. A pasta `docs/` é uma aplicação analítica
legada e não é o destino do gerador de relatórios.

## Como evoluir o projeto

Novas fontes de dados, novos formatos de saída e novas regras devem seguir o mesmo padrão:

- ler em módulo próprio
- validar antes de processar
- processar sem acoplamento com escrita de arquivo
- externalizar novos parâmetros em `config.json`
- registrar a mudança na documentação
- adicionar testes mínimos para a alteração
