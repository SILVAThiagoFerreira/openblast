const embeddedManifestElement = document.getElementById("initial-manifest");
const manifestUrl = resolveManifestUrl();

/* Hexágono de contorno fino (pontas nas laterais) usado como moldura de todos os ícones. */
const HEX_OUTLINE = "M12.5 1h23L47 21 35.5 41h-23L1 21z";

const iconSvg = (content) => `<svg viewBox="0 0 48 42" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" focusable="false" aria-hidden="true"><path d="${HEX_OUTLINE}" />${content}</svg>`;

/* Pictogramas de traço fino (1.3px via non-scaling-stroke no CSS), um por função da ferramenta. */
const icons = {
  flight: () => iconSvg(`
    <path d="M14 15l6 3 6-3 6 3v13l-6-3-6 3-6-3z" />
    <path d="M20 18v13M26 15v13" />
  `),
  charge: () => iconSvg(`
    <rect x="15" y="13" width="7" height="16" rx="3.5" />
    <rect x="26" y="13" width="7" height="16" rx="3.5" />
    <path d="M18.5 18v6M29.5 18v6" />
  `),
  blast: () => iconSvg(`
    <path d="M19 12v14a5 4 0 0 0 10 0V12" />
    <path d="M19 12a5 2 0 0 1 10 0" />
    <path d="M22 18h4M22 22h4" />
  `),
  monitor: () => iconSvg(`
    <rect x="13" y="12" width="22" height="15" rx="1.5" />
    <path d="M16 22h3l2-3 2 5 2-4 1 2h3" />
    <path d="M20 31h8" />
  `),
  waveform: () => iconSvg(`
    <path d="M12 21h5l2-6 3 12 3-16 3 10 2-3h4" />
    <path d="M13 30h22" />
  `),
  standard: () => iconSvg(`
    <path d="M18 12h8l6 6v12H18z" />
    <path d="M26 12v6h6" />
    <path d="M21 24h8M21 28h5" />
  `),
  plan: () => iconSvg(`
    <rect x="13" y="13" width="22" height="18" rx="1.5" />
    <path d="M13 19h22M19 13v4M29 13v4" />
    <path d="M18 26h4M26 26h4" />
  `),
  compass: () => iconSvg(`
    <circle cx="24" cy="21" r="9" />
    <path d="M24 14l3.5 7-3.5-1.5-3.5 1.5z" />
  `),
  bench: () => iconSvg(`
    <path d="M13 30h22" />
    <path d="M17 30v-7M23 30v-12M29 30v-8M35 30v-15" />
  `),
  planned: () => iconSvg(`
    <rect x="13" y="13" width="22" height="16" />
    <path d="M13 19.3h22M13 24.7h22M19.3 13v16M24.7 13v16" />
  `),
  borehole: () => iconSvg(`
    <path d="M16 12v18M32 12v18" />
    <path d="M16 30h16" />
    <path d="M20 16h4M20 21h4M20 26h4" />
  `),
  warning: () => iconSvg(`
    <path d="M24 11l11 20H13z" />
    <path d="M24 18v6" />
    <circle cx="24" cy="27.5" r="0.6" />
  `),
  console: () => iconSvg(`
    <rect x="13" y="14" width="14" height="14" rx="1.5" />
    <rect x="21" y="18" width="14" height="14" rx="1.5" />
    <path d="M16 20h8M16 24h5M24 24h7M24 28h4" />
  `),
  timer: () => iconSvg(`
    <circle cx="24" cy="22" r="8" />
    <path d="M24 22v-4M21 12h6M24 22l3 2" />
  `),
  badge: () => iconSvg(`
    <rect x="13" y="13" width="22" height="16" rx="2" />
    <circle cx="19.5" cy="19" r="2.5" />
    <path d="M25 17h6M25 21h6M17 26h14" />
  `),
  default: () => iconSvg(`
    <path d="M15 16h18M15 21h18M15 26h18" />
    <circle cx="20" cy="16" r="1.6" />
    <circle cx="28" cy="21" r="1.6" />
    <circle cx="22" cy="26" r="1.6" />
  `),
};

function iconForTool(tool) {
  const title = String(tool.formal_title || "").toLowerCase();
  if (tool.kind === "wave") {
    if (title.includes("abnt")) return icons.standard;
    if (title.includes("planejamento")) return icons.plan;
    if (title.includes("waveform")) return icons.waveform;
    return icons.monitor;
  }
  if (tool.kind === "target") {
    if (title.includes("desvios")) return icons.compass;
    if (title.includes("aviso")) return icons.warning;
    if (title.includes("opitdev")) return icons.borehole;
    if (title.includes("previsto")) return icons.planned;
    return icons.bench;
  }
  return icons[tool.kind] || icons.default;
}

const grid = document.getElementById("hub-grid");
let activeGroup = "all";
let searchTerm = "";
let toolCardIndex = 0;
const normalizeSearch = (value) => value.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();

const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (character) => ({
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
  "'": "&#39;",
}[character]));

function setupDirectory(manifest) {
  const groups = Array.isArray(manifest.hubs) ? manifest.hubs : [];
  const toolbar = document.createElement("section");
  toolbar.className = "directory-controls";
  toolbar.setAttribute("aria-label", "Encontrar ferramentas");
  toolbar.innerHTML = `<div class="directory-search"><label class="directory-label" for="tool-search">Buscar ferramenta</label><div class="directory-search__field"><input id="tool-search" type="search" placeholder="Nome, função ou assunto" autocomplete="off" aria-controls="hub-grid"><button type="button" class="search-clear" hidden>Limpar</button></div></div><div class="directory-filter"><label class="directory-label" for="tool-group">Grupo</label><select id="tool-group" aria-controls="hub-grid"><option value="all">Todos os grupos</option></select></div><p id="directory-count" class="directory-count" role="status" aria-live="polite"></p>`;
  const select = toolbar.querySelector("select");
  groups.forEach((group) => select.add(new Option(group.title, group.slug)));
  grid.before(toolbar);
  const empty = document.createElement("div");
  empty.className = "directory-empty";
  empty.hidden = true;
  empty.textContent = "Nenhuma ferramenta encontrada.";
  grid.after(empty);
  const input = toolbar.querySelector("input");
  const clear = toolbar.querySelector("button");
  const apply = () => {
    let visible = 0;
    const cards = grid.querySelectorAll(".tool-card");
    grid.querySelectorAll(".hub-section").forEach((section) => {
      let groupCount = 0;
      section.querySelectorAll(".tool-card").forEach((card) => {
        const searchableText = `${card.textContent} ${card.dataset.searchText || ""}`;
        const matches = (activeGroup === "all" || section.dataset.group === activeGroup) && normalizeSearch(searchableText).includes(searchTerm);
        card.hidden = !matches;
        if (matches) { visible++; groupCount++; }
      });
      section.hidden = groupCount === 0;
    });
    toolbar.querySelector("#directory-count").textContent = `${visible} de ${cards.length} ferramentas`;
    empty.hidden = visible !== 0;
    clear.hidden = !input.value;
  };
  input.addEventListener("input", () => { searchTerm = normalizeSearch(input.value.trim()); apply(); });
  select.addEventListener("change", () => { activeGroup = select.value; apply(); });
  clear.addEventListener("click", () => { input.value = ""; searchTerm = ""; apply(); input.focus(); });
  apply();
}

function resolveManifestUrl() {
  const currentScriptUrl = document.currentScript?.dataset?.manifestUrl;
  if (currentScriptUrl) {
    return currentScriptUrl;
  }

  const pagePath = window.location.pathname.replace(/\\/g, "/");
  if (pagePath.includes("/public/")) {
    return "../output/public/tools_manifest.json";
  }

  if (pagePath.includes("/usvaleverde/")) {
    return "../output/usvaleverde/tools_manifest.json";
  }

  return "output/usvaleverde/tools_manifest.json";
}

function renderStatus(message, modifier = "") {
  grid.innerHTML = `<div class="tool-grid__message${modifier ? ` tool-grid__message--${modifier}` : ""}" role="status">${message}</div>`;
}

/* Ferramentas com status_indicator falso (ex.: em desenvolvimento) ficam em cinza e mostram o status do manifesto. */
function renderToolCard(tool) {
  const title = escapeHtml(tool.formal_title);
  const description = String(tool.description ?? "").trim();
  const fullSearchText = escapeHtml(`${tool.formal_title} ${tool.description}`);
  const descriptionId = `tool-card-description-${++toolCardIndex}`;
  const muted = tool.status_indicator === false;
  const statusLine = muted && tool.status ? `<span class="tool-card__status">${escapeHtml(tool.status)}</span>` : "";
  return `
    <a class="tool-card${muted ? " tool-card--muted" : ""}" data-kind="${escapeHtml(tool.kind || "default")}" data-search-text="${fullSearchText}" href="${escapeHtml(tool.pages_url)}" target="_blank" rel="noopener noreferrer" aria-label="Abrir ${title}" aria-describedby="${descriptionId}">
      <span class="tool-card__hex" aria-hidden="true">${iconForTool(tool)()}</span>
      <span class="tool-card__title">${title}</span>
      ${statusLine}
      <span class="sr-only" id="${descriptionId}">${escapeHtml(description)}</span>
    </a>
  `;
}

function renderHubGroup(group) {
  const cards = group.tools.map((tool) => renderToolCard(tool)).join("");
  const groupSlug = String(group.slug || "group").replace(/[^a-z0-9_-]/gi, "-");
  return `
    <section class="hub-section" data-group="${escapeHtml(group.slug)}" aria-labelledby="hub-${groupSlug}">
      <header class="hub-section__header">
        <h2 id="hub-${groupSlug}">${escapeHtml(group.title)}</h2>
      </header>
      <div class="tool-grid tool-grid--group">${cards}</div>
    </section>
  `;
}

function renderManifest(manifest) {
  const hubs = Array.isArray(manifest.hubs) ? manifest.hubs : [];

  if (!hubs.length) {
    const tools = Array.isArray(manifest.tools) ? manifest.tools : [];
    if (!tools.length) {
      throw new Error("Manifesto sem hubs ou ferramentas.");
    }
    grid.innerHTML = `<section class="hub-section" aria-labelledby="hub-fallback"><header class="hub-section__header"><h2 id="hub-fallback">Ferramentas</h2></header><div class="tool-grid tool-grid--group">${tools.map((tool) => renderToolCard(tool)).join("")}</div></section>`;
    return;
  }

  grid.innerHTML = hubs.map((group) => renderHubGroup(group)).join("");
}

async function loadManifest() {
  grid.setAttribute("aria-busy", "true");
  renderStatus("Carregando manifesto...");

  try {
    if (embeddedManifestElement?.textContent?.trim()) {
      const manifest = JSON.parse(embeddedManifestElement.textContent);
      renderManifest(manifest);
      setupDirectory(manifest);
      return;
    }

    const response = await fetch(manifestUrl, { cache: "default" });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const manifest = await response.json();
    renderManifest(manifest);
    setupDirectory(manifest);
  } catch (error) {
    renderStatus(`Não foi possível carregar o manifesto. ${error.message}`, "error");
  } finally {
    grid.setAttribute("aria-busy", "false");
  }
}

document.addEventListener("DOMContentLoaded", loadManifest);
