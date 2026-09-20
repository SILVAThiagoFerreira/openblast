# Esquema De Dados

## 1. Registro De Entrada Sismográfico

Fonte: CSV exportado do sismógrafo.

| Campo | Tipo | Obrigatório | Significado | Formato | Exemplo válido | Exemplo inválido | Regra |
|---|---|---:|---|---|---|---|---|
| `source_file` | string | sim | nome do arquivo de origem | texto | `20260610-COMUNIDADE DE TORROES.CSV` | vazio | não pode estar vazio |
| `event_date` | string | sim | data do evento | `YYYY-MM-DD` | `2026-06-10` | `10/06/2026` | uma campanha por data |
| `event_time` | string | não | hora do evento | `HH:MM:SS` | `11:58:24` | `11h58` | opcional, mas deve ser coerente quando presente |
| `point_name` | string | sim | ponto monitorado | texto | `COMUNIDADE DE TORROES` | vazio | não pode estar vazio |
| `client` | string | não | cliente do registro | texto | `MVV` | vazio | usado no relatório quando disponível |
| `company` | string | não | empresa associada | texto | `MINERAÇÃO VALE-VERDE` | vazio | informativo |
| `serial_number` | string | não | número de série | texto | `UM16385` | vazio | informativo |
| `calibration` | string | não | data de calibração | texto | `March 26, 2026 by VMA LTDA` | vazio | informativo |
| `gps_distance_m` | number | não | distância GPS | número >= 0 | `1590.0` | `-1` | não pode ser negativo |
| `scaled_distance` | number | não | distância escalonada | número >= 0 | `5028.0` | `-10` | não pode ser negativo |
| `charge_kg` | number | não | carga explosiva | número >= 0 | `0.1` | `-0.1` | não pode ser negativo |
| `pspl_db` | number | sim | pressão sonora de pico | número >= 0 | `110.5` | `-3.0` | obrigatório para o relatório |
| `mic_freq_hz` | number | não | frequência do microfone | número >= 0 | `4.0` | `-1` | opcional |
| `pvs_mm_s` | number | sim | pico vetorial da vibração | número >= 0 | `0.559` | `-0.2` | obrigatório para o relatório |
| `tran_ppv_mm_s` | number | sim | PPV transversal | número >= 0 | `0.473` | `-0.1` | obrigatório para conformidade |
| `vert_ppv_mm_s` | number | sim | PPV vertical | número >= 0 | `0.536` | `-0.1` | obrigatório para conformidade |
| `long_ppv_mm_s` | number | sim | PPV longitudinal | número >= 0 | `0.504` | `-0.1` | obrigatório para conformidade |
| `tran_freq_hz` | number | não | frequência transversal | número >= 0 | `51.2` | `-2` | opcional |
| `vert_freq_hz` | number | não | frequência vertical | número >= 0 | `23.3` | `-2` | opcional |
| `long_freq_hz` | number | não | frequência longitudinal | número >= 0 | `42.7` | `-2` | opcional |
| `tran_time_peak_s` | number | não | tempo do pico transversal | número >= 0 | `125.532` | `-5` | opcional |
| `vert_time_peak_s` | number | não | tempo do pico vertical | número >= 0 | `127.732` | `-5` | opcional |
| `long_time_peak_s` | number | não | tempo do pico longitudinal | número >= 0 | `125.463` | `-5` | opcional |
| `mic_time_peak_s` | number | não | tempo do pico do microfone | número >= 0 | `192.818` | `-5` | opcional |
| `mic_test_result` | string | não | resultado do teste do microfone | texto | `Check` | vazio | informativo |
| `tran_test_result` | string | não | resultado do teste transversal | texto | `Passed` | vazio | informativo |
| `vert_test_result` | string | não | resultado do teste vertical | texto | `Passed` | vazio | informativo |
| `long_test_result` | string | não | resultado do teste longitudinal | texto | `Passed` | vazio | informativo |
| `numeric_qualifiers` | object | não | qualificadores do instrumento preservados para métricas numéricas | mapa campo → `<` ou `>` | `{"pspl_db":"<"}` | `{"pspl_db":"="}` | não altera o valor numérico; evita perder a indicação de limite da fonte |
| `metadata` | object | sim | cabeçalho bruto do CSV | objeto JSON | `{...}` | `null` | rastreabilidade |

### 1.1 Fixtures demonstrativos da versão web

O botão **Carregar exemplo** da aplicação em `pages/` usa três arquivos pequenos
em `pages/assets/examples/`. Eles seguem o mesmo cabeçalho IDFW mínimo aceito
pelo parser (`EventDate`, `TitleNote`/`TitleString`, distâncias, métricas de
pressão/vibração e a linha `Tran,Vert,Long,MicL`), mas são dados demonstrativos
sanitizados. Não substituem os CSVs operacionais fornecidos pelo usuário e não
devem ser usados como evidência de uma campanha real.

## 2. Resumo Processado

| Campo | Tipo | Significado |
|---|---|---|
| `points_count` | integer | quantidade de pontos processados |
| `event_date` | string | data consolidada da campanha |
| `client` | string | cliente exibido no relatório |
| `all_conforme_abnt` | boolean/null | conformidade geral com a norma |
| `all_below_configured_vibration_limit` | boolean/null | conformidade executiva com o limite configurado |
| `max_pspl` | object | maior pressão sonora da campanha; inclui `value_db`, `point_name` e `qualifier` |
| `max_ppv` | object | maior PPV da campanha; inclui `value_mm_s`, `axis`, `point_name` e `qualifier` |
| `max_pvs` | object | maior PVS da campanha; inclui `value_mm_s`, `point_name` e `qualifier` |

## 3. Manifesto De Execução

| Campo | Tipo | Significado |
|---|---|---|
| `output_dir` | string | pasta da execução |
| `pdf` | string | caminho do relatório PDF |
| `png` | string | caminho da imagem do relatório |
| `whatsapp_note` | string | caminho da nota WhatsApp |
| `json` | string | caminho do JSON consolidado |
| `charts` | object | caminhos dos gráficos gerados |
| `manifest` | string | caminho do manifesto salvo |
| `log_file` | string | caminho do log da execução |

## Regras De Validação

- campos obrigatórios não podem ser nulos ou vazios
- números precisam ser finitos e não negativos quando a métrica exigir
- qualificadores, quando presentes, só podem ser `<` ou `>`
- datas devem seguir `YYYY-MM-DD`
- uma execução deve trabalhar com uma única data de evento
- saídas devem ser verificadas após a escrita

## 4. Contrato de nomes e versão web

O relatório e a imagem usam `ENAEX_NSR-YYYYMMDD` com a data consolidada do
evento. A aplicação online acrescenta a nota TXT e reúne os três arquivos em
ZIP, mantendo o mesmo prefixo. A pasta publicada é `docs/` no repositório
`SILVAThiagoFerreira/report-sismografia`; os CSVs selecionados são processados
somente em memória no navegador.
