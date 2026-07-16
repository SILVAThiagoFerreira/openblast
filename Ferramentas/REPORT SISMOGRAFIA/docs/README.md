# Sismografia — site OpenBlast (GitHub Pages)

Site estático que roda 100% no navegador: lê CSVs de sismógrafos (Micromate ISEE) direto no cliente e monta o dashboard técnico de vibração e sobrepressão do desmonte segundo NBR 9653:2018.

O pipeline Python original (`main.py` + `src/`) continua funcionando na pasta pai — este `docs/` é apenas a versão web.

## Como rodar localmente

Qualquer servidor estático serve. Exemplos a partir desta pasta:

```bash
python -m http.server 8080
# ou
npx serve .
```

Abra `http://localhost:8080/`.

## Como publicar no GitHub Pages

1. Suba o repositório para o GitHub.
2. Em **Settings → Pages**, escolha **Source: GitHub Actions**.
3. O workflow `.github/workflows/pages.yml` já está preparado — ele copia esta pasta para a raiz do site e faz o deploy a cada push em `main` que toque `docs/`.
4. Alternativa manual: em **Settings → Pages** escolha **Deploy from branch → main → /docs**. Nesse caso o path precisa ser `Ferramentas/REPORT SISMOGRAFIA/docs`, o que o Pages não suporta direto — prefira o workflow.

## Fluxo de uso

- Por padrão o site carrega uma campanha demo (`data/demo/*.CSV`).
- Botão **Carregar CSVs…** substitui a campanha atual por CSVs escolhidos pelo usuário (tudo processado localmente; nada é enviado a servidor).
- Filtros de ano / mês / ponto / critério NBR reprocessam os gráficos instantaneamente.

## Estrutura

```
docs/
├── index.html         # layout
├── styles.css         # paleta OpenBlast (branco / #38424B / #E20613)
├── assets/
│   └── openblast-logo.png
├── data/demo/         # CSVs de exemplo + manifest.json
└── js/
    ├── parser.js      # equivalente ao src/parser.py
    ├── compliance.js  # curvas NBR / DIN / USBM e avaliação
    ├── charts.js      # todos os gráficos (Chart.js)
    └── app.js         # controller (filtros, KPIs, orquestração)
```

## Trocar a campanha demo

1. Copie os CSVs desejados para `docs/data/demo/`.
2. Edite `docs/data/demo/manifest.json` listando exatamente os nomes dos arquivos.
3. Commit + push. O workflow republica o site.
