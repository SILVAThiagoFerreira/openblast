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

Exemplo de campanha real: a pasta `04.09.2026 - REG` contém um CSV por
ponto (`BARRAGEM DE REJEITOS`, `COMUNIDADE DE TORROES` e `COMUNIDADE DE
ITAPICURU`). A mesma pasta pode ser informada diretamente em `--input`; o
pipeline percorre os CSVs sem alterar os arquivos de origem.

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

Para até três pontos, PDF e PNG são uma única página A4 completa: resumo da
campanha realizada, gráficos normativos e cartões dos pontos na mesma
composição. O escopo informa a quantidade de fontes processadas, a linha de
índice de vibração usa o quadrado verde da referência e a conclusão aparece
antes dos gráficos. Se a campanha tiver mais de três pontos, o PDF acrescenta
páginas de continuação; o PNG continua representando a primeira página.

Os pontos monitorados usam cartões horizontais com status em pill verde e
ícone de conformidade à direita, sem régua vertical adicional. O cabeçalho
usa um marcador circular geométrico simples no canto superior direito.

Os logs ficam em `logs/`.

## Configuração

O arquivo `config.json` centraliza:

- caminhos de entrada, saída e logs
- nomes e templates dos artefatos
- limites técnicos
- parâmetros de gráficos, incluindo a altura vertical compartilhada entre PNG
  Python e Canvas web
- target executivo de vibração e visibilidade da linha “Índices de vibração”
- ordenação dos pontos (`source_order` por padrão, com opção explícita de
  `gps_distance_ascending`)
- geometria, textos e paleta do relatório
- regras de execução

Se um valor precisar mudar, a decisão deve ser feita na configuração, não no código.

Na composição A4 de até três pontos, os gráficos permanecem lado a lado, com
card de 162 pt de altura, distância de 28 pt até o título “Pontos Monitorados”
e raster web de 1430×699 px. O limite superior continua fixo para preservar a
folga da conclusão técnica. A proporção é controlada por
`charts.figure_height=4.4` e compartilhada entre Python e Canvas.

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
5. Abra o PDF e confirme que, para até três pontos, há uma única página A4
   com os títulos `Pressão Sonora x Distância` e `PPV x Limite ABNT`.
6. Rode os testes automatizados com `pytest`.

## Publicação web

O gerador online está publicado em
`https://silvathiagoferreira.github.io/report-sismografia/`. O repositório
dedicado usa GitHub Pages em `main:/docs`; por isso, `pages/` é a fonte de
trabalho local e `docs/` é a cópia publicada que deve ser atualizada antes do
push. O navegador lê e valida os CSVs localmente, monta PDF, PNG, TXT e ZIP,
e nunca envia os dados de barragens ou comunidades para um backend.

As versões Python e web compartilham o contrato de nomes:
`ENAEX_NSR-YYYYMMDD.pdf`, `ENAEX_NSR-YYYYMMDD.png` e
`ENAEX_NSR-YYYYMMDD_nota_whatsapp.txt`.

## Como evoluir o projeto

Novas fontes de dados, novos formatos de saída e novas regras devem seguir o mesmo padrão:

- ler em módulo próprio
- validar antes de processar
- processar sem acoplamento com escrita de arquivo
- externalizar novos parâmetros em `config.json`
- registrar a mudança na documentação
- adicionar testes mínimos para a alteração
