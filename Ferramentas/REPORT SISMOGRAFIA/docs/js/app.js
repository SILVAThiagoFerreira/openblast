/* App controller: carrega dados (demo embutida ou upload), aplica filtros,
 * renderiza KPIs e delega os gráficos a SismoCharts.
 */
(function () {
  'use strict';

  var STATE = {
    all: [],           // registros parseados
    curve: 'nbr9653',
    year: '', month: '', point: ''
  };

  var $ = function (id) { return document.getElementById(id); };

  // -------- Data loading --------
  function loadDemo() {
    return fetch('data/demo/manifest.json', { cache: 'no-store' })
      .then(function (r) {
        if (!r.ok) throw new Error('sem demo');
        return r.json();
      })
      .then(function (manifest) {
        var files = (manifest && manifest.files) || [];
        return Promise.all(files.map(function (name) {
          return fetch('data/demo/' + encodeURIComponent(name))
            .then(function (r) { return r.text(); })
            .then(function (text) { return SismoParser.parseSismoCsv(name, text); });
        }));
      });
  }

  function loadFromFiles(fileList) {
    var arr = Array.from(fileList).filter(function (f) { return /\.csv$/i.test(f.name); });
    return Promise.all(arr.map(function (f) {
      return f.text().then(function (text) { return SismoParser.parseSismoCsv(f.name, text); });
    }));
  }

  // -------- Filters --------
  function unique(arr) { return Array.from(new Set(arr)).filter(function (v) { return v != null && v !== ''; }); }

  function refreshFilterOptions() {
    var years  = unique(STATE.all.map(function (r) { return r.event_iso ? r.event_iso.slice(0,4) : null; })).sort();
    var months = unique(STATE.all.map(function (r) { return r.event_iso ? r.event_iso.slice(5,7) : null; })).sort();
    var points = unique(STATE.all.map(function (r) { return r.point_name; })).sort();

    fillSelect($('f-year'),  years,  'Todos os anos');
    fillSelect($('f-month'), months.map(function (m) { return { v: m, label: monthLabel(m) }; }), 'Todos os meses');
    fillSelect($('f-point'), points, 'Todos os pontos');
  }
  function monthLabel(m) {
    var names = ['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez'];
    var i = parseInt(m, 10) - 1;
    return (i >= 0 && i < 12) ? (names[i] + ' (' + m + ')') : m;
  }
  function fillSelect(sel, options, allLabel) {
    var current = sel.value;
    sel.innerHTML = '';
    var opt = document.createElement('option'); opt.value = ''; opt.textContent = allLabel;
    sel.appendChild(opt);
    options.forEach(function (o) {
      var el = document.createElement('option');
      if (typeof o === 'string') { el.value = o; el.textContent = o; }
      else                       { el.value = o.v; el.textContent = o.label; }
      sel.appendChild(el);
    });
    if (Array.from(sel.options).some(function (o) { return o.value === current; })) sel.value = current;
  }

  function applyFilters(records) {
    return records.filter(function (r) {
      if (STATE.year  && (!r.event_iso || r.event_iso.slice(0,4) !== STATE.year))  return false;
      if (STATE.month && (!r.event_iso || r.event_iso.slice(5,7) !== STATE.month)) return false;
      if (STATE.point && r.point_name !== STATE.point) return false;
      return true;
    });
  }

  // -------- KPIs --------
  function fmt(v, digits) {
    if (v == null || isNaN(v)) return '—';
    return v.toLocaleString('pt-BR', { minimumFractionDigits: digits, maximumFractionDigits: digits });
  }
  function updateKPIs(records) {
    $('kpi-events').textContent = records.length.toLocaleString('pt-BR');
    $('kpi-events-foot').textContent = records.length + ' eventos após filtro';

    var withPpv = records.map(function (r) {
      var d = SismoCompliance.dominantAxis(r);
      return d ? { v: d.ppv, f: d.freq, name: r.point_name } : null;
    }).filter(Boolean);
    var maxPpv = withPpv.reduce(function (a, b) { return a && a.v > b.v ? a : b; }, null);
    $('kpi-ppv').textContent = maxPpv ? fmt(maxPpv.v, 2) + ' mm/s' : '—';
    var lim = maxPpv ? SismoCompliance.interpolateLimit(maxPpv.f, SismoCompliance.CURVES.nbr9653) : null;
    $('kpi-ppv-foot').textContent = maxPpv
      ? 'NBR 9653 @ ' + fmt(maxPpv.f, 1) + ' Hz: ' + fmt(lim, 1) + ' mm/s'
      : ' ';

    var evaluated = records.map(function (r) { return SismoCompliance.evaluate(r, STATE.curve); });
    var judged = evaluated.filter(function (e) { return e.conforme != null; });
    var ok = judged.filter(function (e) { return e.conforme; }).length;
    var pct = judged.length ? (ok / judged.length * 100) : null;
    $('kpi-conf').textContent = pct == null ? '—' : fmt(pct, 1) + '%';
    $('kpi-conf-foot').textContent = judged.length ? (ok + ' de ' + judged.length + ' abaixo de ' + labelCurve(STATE.curve)) : ' ';
    $('kpi-conf').classList.toggle('alert', pct != null && pct < 100);

    var maxAir = records.reduce(function (a, r) { return (r.pspl_db != null && (!a || r.pspl_db > a.pspl_db)) ? r : a; }, null);
    $('kpi-air').textContent = maxAir ? fmt(maxAir.pspl_db, 1) + ' dBL' : '—';
    var above = records.filter(function (r) { return r.pspl_db != null && r.pspl_db > 134; }).length;
    $('kpi-air-foot').textContent = above ? (above + ' acima de 134 dBL (NBR)') : 'Abaixo de 134 dBL';
    $('kpi-air').classList.toggle('alert', above > 0);
  }
  function labelCurve(k) {
    return {
      'nbr9653': 'NBR 9653',
      'din4150-2': 'DIN 4150-3 L2',
      'din4150-3': 'DIN 4150-3 L3',
      'usbm': 'USBM RI 8507'
    }[k] || k;
  }

  // -------- Chips --------
  function updateChips() {
    var chips = [];
    chips.push({ id: 'crit', label: 'Critério: ' + labelCurve(STATE.curve), removable: false });
    if (STATE.year)  chips.push({ id: 'year',  label: 'Ano: '   + STATE.year });
    if (STATE.month) chips.push({ id: 'month', label: 'Mês: '   + monthLabel(STATE.month) });
    if (STATE.point) chips.push({ id: 'point', label: 'Ponto: ' + STATE.point });
    var wrap = $('chip-row');
    wrap.innerHTML = '';
    chips.forEach(function (c) {
      var el = document.createElement('span');
      el.className = 'chip';
      el.textContent = c.label;
      if (c.removable !== false) {
        var x = document.createElement('span');
        x.className = 'x'; x.textContent = '×';
        x.onclick = function () {
          if (c.id === 'year')  { STATE.year  = ''; $('f-year').value  = ''; }
          if (c.id === 'month') { STATE.month = ''; $('f-month').value = ''; }
          if (c.id === 'point') { STATE.point = ''; $('f-point').value = ''; }
          render();
        };
        el.appendChild(document.createTextNode(' '));
        el.appendChild(x);
      }
      wrap.appendChild(el);
    });
  }

  // -------- Render --------
  function render() {
    var filtered = applyFilters(STATE.all);
    $('event-count').textContent = filtered.length + ' eventos carregados' + (filtered.length !== STATE.all.length ? ' (' + STATE.all.length + ' totais)' : '');
    $('updated').textContent = 'Atualizado em ' + new Date().toLocaleString('pt-BR');

    // Contexto no header: primeiro registro dá o cliente
    var ctx = (filtered[0] && (filtered[0].company || filtered[0].client)) || '';
    $('ctx-client').textContent = ctx.toUpperCase();

    updateChips();
    updateKPIs(filtered);
    SismoCharts.renderAll(filtered, STATE.curve);
  }

  // -------- Wire up --------
  function bind() {
    $('f-year').addEventListener('change',  function (e) { STATE.year  = e.target.value; render(); });
    $('f-month').addEventListener('change', function (e) { STATE.month = e.target.value; render(); });
    $('f-point').addEventListener('change', function (e) { STATE.point = e.target.value; render(); });
    $('f-crit').addEventListener('change',  function (e) { STATE.curve = e.target.value; render(); });
    $('btn-clear').addEventListener('click', function () {
      STATE.year = ''; STATE.month = ''; STATE.point = '';
      $('f-year').value = ''; $('f-month').value = ''; $('f-point').value = '';
      render();
    });
    $('f-file').addEventListener('change', function (e) {
      if (!e.target.files || !e.target.files.length) return;
      $('event-count').textContent = 'Lendo ' + e.target.files.length + ' arquivo(s)…';
      loadFromFiles(e.target.files).then(function (recs) {
        STATE.all = recs;
        refreshFilterOptions();
        render();
      }).catch(function (err) {
        console.error(err);
        $('event-count').textContent = 'Falha ao ler CSVs: ' + err.message;
      });
    });
  }

  function boot() {
    bind();
    loadDemo().then(function (recs) {
      STATE.all = recs || [];
      refreshFilterOptions();
      render();
    }).catch(function () {
      // Sem demo — mostra estado vazio
      STATE.all = [];
      refreshFilterOptions();
      render();
      $('event-count').textContent = 'Sem dados. Use "Carregar CSVs…" para começar.';
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
