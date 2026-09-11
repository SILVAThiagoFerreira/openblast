const embeddedManifestElement = document.getElementById("initial-manifest");
const manifestUrl = resolveManifestUrl();

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
  shield: () => `
    <svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true">
      <path d="M32 10l16 6v12c0 12-8 20-16 26-8-6-16-14-16-26V16l16-6z" />
      <path d="M24 33l6 6 11-13" />
    </svg>
  `,
  default: () => `
    <svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true">
      <rect x="14" y="14" width="36" height="36" rx="12" />
      <path d="M22 32h20" />
      <path d="M32 22v20" />
    </svg>
  `,
};

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
      <span class="tool-card__hex" aria-hidden="true">${(icons[tool.kind] || icons.default)()}</span>
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
