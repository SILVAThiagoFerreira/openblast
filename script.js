const embeddedManifestElement = document.getElementById("initial-manifest");
const manifestUrl = resolveManifestUrl();

const iconSvg = (content) => `<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${content}</svg>`;

const icons = {
  flight: () => iconSvg(`
    <path d="M12 46c7-10 15-16 24-18 6-1 11 0 16 3" />
    <path d="M38 17l13 14-18 1 5-7z" fill="currentColor" stroke="none" />
    <circle cx="17" cy="40" r="2" fill="currentColor" stroke="none" />
    <circle cx="27" cy="34" r="2" fill="currentColor" stroke="none" />
    <circle cx="39" cy="29" r="2" fill="currentColor" stroke="none" />
    <path d="M15 51h34" opacity="0.45" />
  `),
  charge: () => iconSvg(`
    <rect x="17" y="13" width="10" height="38" rx="5" />
    <rect x="37" y="13" width="10" height="38" rx="5" />
    <path d="M22 19v7M22 35v7M42 19v7M42 35v7" />
    <path d="M31 21l-4 9h6l-4 12" stroke-width="3" />
  `),
  blast: () => iconSvg(`
    <path d="M16 15v30" />
    <path d="M24 20v25M32 24v21M40 29v16" />
    <path d="M12 46h40" />
    <path d="M11 51h42M15 56h34" opacity="0.58" />
    <path d="M13 15h8M21 20h8M29 24h8M37 29h8" />
    <path d="M48 14l1.6 3.4L53 19l-3.4 1.6L48 24l-1.6-3.4L43 19l3.4-1.6z" fill="currentColor" stroke="none" />
  `),
  monitor: () => iconSvg(`
    <path d="M10 35h8l4-10 7 22 7-28 6 16h12" />
    <path d="M16 18v6M48 18v6M12 49h40" opacity="0.52" />
    <circle cx="29" cy="47" r="2.2" fill="currentColor" stroke="none" />
  `),
  waveform: () => iconSvg(`
    <path d="M10 36h7l4-7 5 14 6-24 6 32 6-15 4 6h8" />
    <path d="M12 18h40M12 52h40" opacity="0.38" />
    <path d="M18 15v6M46 15v6" />
  `),
  standard: () => iconSvg(`
    <path d="M19 11h20l8 8v34H19z" />
    <path d="M39 11v10h8" />
    <path d="M25 30h16M25 37h16M25 44h10" />
    <path d="M43 44l3 3 6-7" />
  `),
  plan: () => iconSvg(`
    <path d="M12 43c7-8 13-11 20-11s14 3 20-8" />
    <circle cx="12" cy="43" r="3" />
    <circle cx="32" cy="32" r="3" />
    <circle cx="52" cy="24" r="3" />
    <path d="M32 18v8M28 22h8M12 52h40" opacity="0.62" />
  `),
  compass: () => iconSvg(`
    <circle cx="32" cy="34" r="17" />
    <path d="M32 10v7M32 51v5M8 34h7M49 34h7" />
    <path d="M37 29l9-9-12 4-9 9 12-4z" fill="currentColor" stroke="none" />
    <circle cx="32" cy="34" r="3" />
  `),
  bench: () => iconSvg(`
    <path d="M12 47h40M12 39h38M18 31h32M24 23h24" />
    <path d="M18 47V28M30 47V21M42 47V26" />
    <path d="M14 53h36" opacity="0.55" />
  `),
  borehole: () => iconSvg(`
    <path d="M19 12h26" />
    <path d="M22 12v39M42 12v39" />
    <path d="M22 20h20M22 29h20M22 38h20M22 47h20" opacity="0.65" />
    <path d="M15 16h7M15 25h7M15 34h7M15 43h7" />
    <path d="M42 17l8 8-8 8" />
  `),
  warning: () => iconSvg(`
    <path d="M32 10l23 42H9z" />
    <path d="M32 24v13" stroke-width="3" />
    <circle cx="32" cy="44" r="1.8" fill="currentColor" stroke="none" />
    <path d="M15 55h34" opacity="0.5" />
  `),
  console: () => iconSvg(`
    <rect x="11" y="16" width="27" height="31" rx="3" />
    <rect x="26" y="23" width="27" height="31" rx="3" />
    <path d="M18 25h13M18 32h13M18 39h8M33 32h13M33 39h13M33 46h8" />
    <path d="M38 12v7M34 15h8" />
  `),
  timer: () => iconSvg(`
    <circle cx="32" cy="35" r="18" />
    <path d="M26 11h12M32 17v-6M24 16l-4-4M40 16l4-4" />
    <path d="M32 25v11l7 4" />
    <path d="M10 35h6M48 35h6" opacity="0.7" />
  `),
  default: () => iconSvg(`
    <path d="M15 20h34M15 32h34M15 44h34" />
    <circle cx="25" cy="20" r="4" fill="currentColor" stroke="none" />
    <circle cx="40" cy="32" r="4" fill="currentColor" stroke="none" />
    <circle cx="29" cy="44" r="4" fill="currentColor" stroke="none" />
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
    return icons.bench;
  }
  return icons[tool.kind] || icons.default;
}

const grid = document.getElementById("hub-grid");
let activeGroup = "all";
let searchTerm = "";
const normalizeSearch = (value) => value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();

const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (character) => ({
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
  "'": "&#39;",
}[character]));

function truncateDescription(value, maxLength = 100) {
  const text = String(value ?? "").trim();
  if (text.length <= maxLength) return text;
  return `${text.slice(0, maxLength - 1).trimEnd()}…`;
}

function setupDirectory(manifest) {
  const groups = Array.isArray(manifest.hubs) ? manifest.hubs : [];
  const toolbar = document.createElement("section");
  toolbar.className = "directory-controls";
  toolbar.setAttribute("aria-label", "Encontrar ferramentas");
  toolbar.innerHTML = `<div class="directory-search"><label for="tool-search">Buscar ferramenta</label><div class="directory-search__field"><input id="tool-search" type="search" placeholder="Nome, atividade ou formato de arquivo" autocomplete="off" aria-controls="hub-grid"><button type="button" class="search-clear" hidden>Limpar</button></div></div><div class="directory-filter"><label for="tool-group">Grupo</label><select id="tool-group" aria-controls="hub-grid"><option value="all">Todos os grupos</option></select></div><p id="directory-count" class="directory-count" role="status" aria-live="polite"></p>`;
  const select = toolbar.querySelector("select");
  groups.forEach((group) => select.add(new Option(group.title, group.slug)));
  grid.before(toolbar);
  const empty = document.createElement("div");
  empty.className = "directory-empty";
  empty.hidden = true;
  empty.textContent = "Nenhuma ferramenta encontrada. Tente outro termo ou selecione todos os grupos.";
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

function renderToolCard(tool) {
  const title = escapeHtml(tool.formal_title);
  const description = truncateDescription(tool.description);
  const fullSearchText = escapeHtml(`${tool.formal_title} ${tool.description}`);
  return `
    <a class="tool-card" data-kind="${escapeHtml(tool.kind || "default")}" data-search-text="${fullSearchText}" href="${escapeHtml(tool.pages_url)}" target="_blank" rel="noopener noreferrer" aria-label="Abrir ${title}. ${escapeHtml(description)}">
      <span class="tool-card__hex" aria-hidden="true">${iconForTool(tool)()}</span>
      <h3>${title}</h3>
      <p>${escapeHtml(description)}</p>
    </a>
  `;
}

function renderHubGroup(group) {
  const cards = group.tools.map((tool) => renderToolCard(tool)).join("");
  return `
    <section class="hub-section" data-group="${group.slug}" aria-labelledby="hub-${group.slug}">
      <header class="hub-section__header">
        <h2 id="hub-${group.slug}">${group.title}</h2>
        <p>${group.description}</p>
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
    grid.innerHTML = `<section class="hub-section" aria-labelledby="hub-fallback"><header class="hub-section__header"><h2 id="hub-fallback">Ferramentas</h2><p class="section-head__text">Agrupamento único herdado do formato anterior.</p></header><div class="tool-grid tool-grid--group">${tools.map((tool) => renderToolCard(tool)).join("")}</div></section>`;
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
