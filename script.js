const manifestUrl = "output/tools_manifest.json";

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
  default: () => `
    <svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true">
      <rect x="14" y="14" width="36" height="36" rx="12" />
      <path d="M22 32h20" />
      <path d="M32 22v20" />
    </svg>
  `,
};

const grid = document.getElementById("tool-grid");

const renderLogo = (kind) => (icons[kind] || icons.default)();

function renderStatus(message, modifier = "") {
  grid.innerHTML = `<div class="tool-grid__message${modifier ? ` tool-grid__message--${modifier}` : ""}" role="status">${message}</div>`;
}

function renderTools(tools) {
  grid.innerHTML = tools
    .map((tool, index) => `
      <article class="tool-card reveal" style="--accent: ${tool.accent}; --accent-2: ${tool.accent2}; --delay: ${index * 90}ms;">
        <div class="tool-card__head">
          <div class="tool-mark" aria-hidden="true">${renderLogo(tool.kind)}</div>
        </div>
        <h3>${tool.formal_title}</h3>
        <p>${tool.description}</p>
        <div class="tool-card__actions">
          <a class="tool-link tool-link--primary" href="${tool.pages_url}" target="_blank" rel="noreferrer">Abrir página</a>
          <a class="tool-link" href="${tool.github_url}" target="_blank" rel="noreferrer">GitHub</a>
        </div>
      </article>
    `)
    .join("");
}

async function loadManifest() {
  grid.setAttribute("aria-busy", "true");
  renderStatus("Carregando ferramentas...");

  try {
    const response = await fetch(`${manifestUrl}?v=${Date.now()}`, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const manifest = await response.json();
    const tools = Array.isArray(manifest.tools) ? manifest.tools : [];

    if (!tools.length) {
      throw new Error("Manifesto sem ferramentas.");
    }

    renderTools(tools);
  } catch (error) {
    renderStatus(`Não foi possível carregar o manifesto. ${error.message}`, "error");
  } finally {
    grid.setAttribute("aria-busy", "false");
  }
}

document.addEventListener("DOMContentLoaded", loadManifest);
