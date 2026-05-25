const tools = [
  {
    repo: "enaex-plano-de-voo",
    title: "Conversor DXF para Poligonal no Google Earth com Exportação KMZ",
    description:
      "Converte DXF em poligonal pronta para visualização no Google Earth e exporta KMZ para uso operacional.",
    github: "https://github.com/SILVAThiagoFerreira/enaex-plano-de-voo",
    pages: "https://silvathiagoferreira.github.io/enaex-plano-de-voo/",
    kind: "flight",
    accent: "#e20313",
    accent2: "#ff7a24",
  },
  {
    repo: "usmvv_planned_and_executed_data_consolidation",
    title: "US Vale Verde PLAN/EXEC Data Console",
    description:
      "Painel de consolidação visual para dados planejados e executados da operação US Vale Verde.",
    github: "https://github.com/SILVAThiagoFerreira/usmvv_planned_and_executed_data_consolidation",
    pages: "https://silvathiagoferreira.github.io/usmvv_planned_and_executed_data_consolidation/",
    kind: "console",
    accent: "#e20313",
    accent2: "#6c8cff",
  },
  {
    repo: "temposemovimentos",
    title: "Sistema de Tempos e Movimentos",
    description:
      "Aplicação para apoio ao estudo e acompanhamento de tempos e movimentos com visual direto.",
    github: "https://github.com/SILVAThiagoFerreira/temposemovimentos",
    pages: "https://silvathiagoferreira.github.io/temposemovimentos/",
    kind: "timer",
    accent: "#e20313",
    accent2: "#ffb12a",
  },
  {
    repo: "blasthole-profile-creator",
    title: "Blasthole Profile Creator",
    description:
      "Ferramenta para criação e leitura de perfis de blastholes com foco em clareza operacional.",
    github: "https://github.com/SILVAThiagoFerreira/blasthole-profile-creator",
    pages: "https://silvathiagoferreira.github.io/blasthole-profile-creator/",
    kind: "blast",
    accent: "#e20313",
    accent2: "#8dd3ff",
  },
  {
    repo: "pfr-enaex",
    title: "PFR - Plano de Fogo Realizado",
    description:
      "Hub para registro e consulta do plano de fogo realizado com leitura rápida e padronizada.",
    github: "https://github.com/SILVAThiagoFerreira/pfr-enaex",
    pages: "https://silvathiagoferreira.github.io/pfr-enaex/",
    kind: "target",
    accent: "#e20313",
    accent2: "#ff5b35",
  },
  {
    repo: "aquickreportofseismographicdata",
    title: "Report Sismografia Enaex",
    description:
      "Relatório rápido para dados sismográficos, com foco em consulta visual objetiva e limpa.",
    github: "https://github.com/SILVAThiagoFerreira/aquickreportofseismographicdata",
    pages: "https://silvathiagoferreira.github.io/aquickreportofseismographicdata/",
    kind: "wave",
    accent: "#e20313",
    accent2: "#37c6b3",
  },
];

const icons = {
  flight: () => `
    <svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true">
      <path d="M11 43c6-8 13-13 21-15s16-1 21 3" />
      <path d="M37 18l12 12-16 2z" fill="currentColor" stroke="none" />
      <circle cx="19" cy="36" r="2.2" fill="currentColor" stroke="none" />
      <circle cx="29" cy="32" r="2.2" fill="currentColor" stroke="none" />
      <circle cx="40" cy="28" r="2.2" fill="currentColor" stroke="none" />
      <path d="M26 45l6 5 7-12" />
    </svg>
  `,
  console: () => `
    <svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true">
      <path d="M12 42h40" />
      <path d="M17 38v10M25 29v19M33 24v24M41 30v18M49 34v14" />
      <path d="M14 23c6 3 11 4 17 1s11-2 15 1" />
      <path d="M43 16l6 6-8 1z" fill="currentColor" stroke="none" />
    </svg>
  `,
  timer: () => `
    <svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true">
      <circle cx="32" cy="35" r="18" />
      <path d="M24 16h16" />
      <path d="M32 28v8l6 4" />
      <path d="M21 16l-4-4M43 16l4-4" />
      <path d="M15 35h5M44 35h5" />
    </svg>
  `,
  blast: () => `
    <svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true">
      <path d="M11 43l10-7 10 3 11-8 9 2" />
      <path d="M11 50l10-7 10 3 11-8 9 2" opacity="0.7" />
      <circle cx="18" cy="55" r="2.2" fill="currentColor" stroke="none" />
      <circle cx="28" cy="50" r="2.2" fill="currentColor" stroke="none" />
      <circle cx="39" cy="53" r="2.2" fill="currentColor" stroke="none" />
      <circle cx="50" cy="45" r="2.2" fill="currentColor" stroke="none" />
    </svg>
  `,
  target: () => `
    <svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true">
      <circle cx="32" cy="32" r="18" />
      <circle cx="32" cy="32" r="10" />
      <circle cx="32" cy="32" r="3" fill="currentColor" stroke="none" />
      <path d="M42 22l10-10" />
      <path d="M44 12h8v8" />
    </svg>
  `,
  wave: () => `
    <svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true">
      <path d="M10 36h8l5-12 7 28 7-18 5 10h12" />
      <path d="M12 24h40" opacity="0.35" />
      <path d="M12 48h40" opacity="0.35" />
    </svg>
  `,
};

const grid = document.getElementById("tool-grid");
const toolCountTargets = document.querySelectorAll("[data-tool-count]");
const linkCountTargets = document.querySelectorAll("[data-link-count]");

const renderLogo = (kind) => icons[kind]();

grid.innerHTML = tools
  .map((tool, index) => `
      <article class="tool-card reveal" style="--accent: ${tool.accent}; --accent-2: ${tool.accent2}; --delay: ${index * 90}ms;">
        <div class="tool-card__head">
          <div class="tool-mark" aria-hidden="true">${renderLogo(tool.kind)}</div>
          <p class="tool-card__slug">${tool.repo}</p>
        </div>
        <h3>${tool.title}</h3>
        <p>${tool.description}</p>
        <div class="tool-card__actions">
          <a class="tool-link tool-link--primary" href="${tool.pages}" target="_blank" rel="noreferrer">Abrir page</a>
          <a class="tool-link" href="${tool.github}" target="_blank" rel="noreferrer">GitHub</a>
        </div>
      </article>
    `)
  .join("");

toolCountTargets.forEach((node) => {
  node.textContent = String(tools.length);
});

linkCountTargets.forEach((node) => {
  node.textContent = String(tools.length * 2);
});
