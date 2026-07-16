/* Renderização de todos os gráficos com Chart.js.
 * Paleta discreta: fundo branco, cinza tinta #38424B, acento vermelho #E20613.
 * Nada de gradientes, glow ou animações teatrais.
 */
(function () {
  'use strict';

  var INK      = '#38424B';
  var INK_MUTE = '#8a9199';
  var LINE     = '#e6e7ea';
  var RED      = '#E20613';
  var BLUE     = '#4a6ea8';
  var VIOLET   = '#6b57a8';

  // Estado dos gráficos por id de canvas — permite destruir/recriar sem vazamento.
  var CHARTS = {};

  function destroy(id) {
    if (CHARTS[id]) { CHARTS[id].destroy(); delete CHARTS[id]; }
  }

  function mount(id, config) {
    destroy(id);
    var el = document.getElementById(id);
    if (!el) return;
    CHARTS[id] = new Chart(el.getContext('2d'), config);
  }

  Chart.defaults.font.family = getComputedStyle(document.body).getPropertyValue('font-family') || 'sans-serif';
  Chart.defaults.font.size = 11;
  Chart.defaults.color = INK;
  Chart.defaults.borderColor = LINE;
  Chart.defaults.animation = false;
  Chart.defaults.responsive = true;
  Chart.defaults.maintainAspectRatio = false;

  var TOOLTIP = {
    backgroundColor: 'rgba(56, 66, 75, 0.95)',
    titleColor: '#fff',
    bodyColor: '#fff',
    borderColor: 'transparent',
    padding: 8,
    displayColors: false,
    titleFont: { weight: '600', size: 11 },
    bodyFont: { size: 11 }
  };

  // --------- Utilidades ---------
  function sampleCurve(curve, xs) {
    return xs.map(function (x) { return { x: x, y: SismoCompliance.interpolateLimit(x, curve) }; });
  }
  function logTicksHz() {
    return [1, 2, 5, 10, 20, 50, 100, 200, 250];
  }

  // --------- 1. Velocidade × Frequência ---------
  function velocityFrequency(records, curveKey) {
    var xsLog = [];
    for (var x = 1; x <= 250; x *= 1.06) xsLog.push(x);
    xsLog.push(250);

    var criterion = SismoCompliance.CURVES[curveKey];
    var criterionLine = sampleCurve(criterion, xsLog);

    var eventPoints = records.map(function (r) {
      var d = SismoCompliance.dominantAxis(r);
      if (!d || d.ppv == null || d.freq == null) return null;
      return { x: d.freq, y: d.ppv };
    }).filter(Boolean);

    mount('ch-vxf', {
      type: 'scatter',
      data: {
        datasets: [
          {
            label: 'NBR 9653:2018 (critério)',
            type: 'line',
            data: sampleCurve(SismoCompliance.CURVES['nbr9653'], xsLog),
            borderColor: RED, borderWidth: 2, pointRadius: 0, tension: 0
          },
          {
            label: 'DIN 4150-3 · Linha 2 (residencial)',
            type: 'line',
            data: sampleCurve(SismoCompliance.CURVES['din4150-2'], xsLog),
            borderColor: '#4c8f3b', borderWidth: 1.2, borderDash: [5,4], pointRadius: 0
          },
          {
            label: 'DIN 4150-3 · Linha 3 (sensível)',
            type: 'line',
            data: sampleCurve(SismoCompliance.CURVES['din4150-3'], xsLog),
            borderColor: BLUE, borderWidth: 1.2, borderDash: [5,4], pointRadius: 0
          },
          {
            label: 'USBM RI 8507 (modern homes)',
            type: 'line',
            data: sampleCurve(SismoCompliance.CURVES['usbm'], xsLog),
            borderColor: '#7d8fb3', borderWidth: 1.2, borderDash: [2,3], pointRadius: 0
          },
          {
            label: 'Eventos',
            data: eventPoints,
            backgroundColor: 'rgba(56, 66, 75, 0.55)',
            borderColor: 'rgba(56, 66, 75, 0.7)',
            pointRadius: 2.5, pointHoverRadius: 4
          }
        ]
      },
      options: {
        scales: {
          x: {
            type: 'logarithmic', min: 1, max: 250,
            title: { display: true, text: 'Frequência dominante (Hz)', color: INK_MUTE },
            grid: { color: LINE }, border: { color: LINE },
            ticks: {
              color: INK_MUTE,
              callback: function (v) { return logTicksHz().indexOf(v) >= 0 ? v : ''; }
            }
          },
          y: {
            type: 'logarithmic', min: 0.5, max: 100,
            title: { display: true, text: 'Velocidade resultante — PPV (mm/s)', color: INK_MUTE },
            grid: { color: LINE }, border: { color: LINE },
            ticks: {
              color: INK_MUTE,
              callback: function (v) { return [1,2,5,10,20,50,100].indexOf(v) >= 0 ? v : ''; }
            }
          }
        },
        plugins: {
          legend: { position: 'bottom', labels: { color: INK, boxWidth: 14, boxHeight: 2, usePointStyle: false } },
          tooltip: Object.assign({}, TOOLTIP, {
            callbacks: {
              label: function (c) {
                if (c.dataset.label === 'Eventos') {
                  return c.parsed.y.toFixed(2) + ' mm/s @ ' + c.parsed.x.toFixed(1) + ' Hz';
                }
                return c.dataset.label + ': ' + c.parsed.y.toFixed(1) + ' mm/s @ ' + c.parsed.x.toFixed(1) + ' Hz';
              }
            }
          })
        }
      }
    });
  }

  // --------- 2. PPV por evento (temporal) ---------
  function ppvByEvent(records, curveKey) {
    var sorted = records.slice().filter(function (r) { return r.event_iso; })
      .sort(function (a, b) { return a.event_iso.localeCompare(b.event_iso); });
    var pts = sorted.map(function (r) {
      var e = SismoCompliance.evaluate(r, curveKey);
      if (e.ppv_ref == null) return null;
      return {
        x: r.event_iso, y: e.ppv_ref,
        conforme: e.conforme, point: r.point_name
      };
    }).filter(Boolean);

    mount('ch-ppv', {
      type: 'scatter',
      data: {
        datasets: [{
          label: 'PPV por evento (cor = conformidade)',
          data: pts,
          parsing: false,
          pointRadius: 2.5,
          pointBackgroundColor: pts.map(function (p) { return p.conforme === false ? RED : 'rgba(56, 66, 75, 0.55)'; }),
          pointBorderColor:    pts.map(function (p) { return p.conforme === false ? RED : 'rgba(56, 66, 75, 0.7)';  })
        }]
      },
      options: {
        parsing: false,
        scales: {
          x: {
            type: 'time',
            time: { unit: pickTimeUnit(sorted) },
            grid: { color: LINE }, border: { color: LINE }, ticks: { color: INK_MUTE }
          },
          y: {
            beginAtZero: true, title: { display: true, text: 'PPV (mm/s)', color: INK_MUTE },
            grid: { color: LINE }, border: { color: LINE }, ticks: { color: INK_MUTE }
          }
        },
        plugins: {
          legend: { position: 'bottom', labels: { color: INK, boxWidth: 14, boxHeight: 2 } },
          tooltip: Object.assign({}, TOOLTIP, {
            callbacks: {
              label: function (c) {
                var p = c.raw;
                return [ p.point, p.y.toFixed(3) + ' mm/s', p.conforme === false ? '× acima do critério' : '✓ dentro do critério' ];
              },
              title: function (items) { return new Date(items[0].raw.x).toLocaleDateString('pt-BR'); }
            }
          })
        }
      }
    });
  }

  // --------- 3. Airblast por evento ---------
  function airblastByEvent(records) {
    var sorted = records.slice().filter(function (r) { return r.event_iso && r.pspl_db != null; })
      .sort(function (a, b) { return a.event_iso.localeCompare(b.event_iso); });
    var pts = sorted.map(function (r) {
      return { x: r.event_iso, y: r.pspl_db, point: r.point_name, ok: r.pspl_db <= 134 };
    });

    mount('ch-air', {
      type: 'scatter',
      data: {
        datasets: [
          {
            label: '134 dBL — limite NBR 9653', type: 'line',
            data: linePairs(sorted, 134),
            borderColor: RED, borderWidth: 1.4, borderDash: [4,3], pointRadius: 0, parsing: false
          },
          {
            label: '133 dBL — USBM/OSMRE',      type: 'line',
            data: linePairs(sorted, 133),
            borderColor: BLUE, borderWidth: 1.0, borderDash: [3,3], pointRadius: 0, parsing: false
          },
          {
            label: '129 dBL — sensível / incômodo', type: 'line',
            data: linePairs(sorted, 129),
            borderColor: '#7d8fb3', borderWidth: 1.0, borderDash: [2,3], pointRadius: 0, parsing: false
          },
          {
            label: 'Airblast por evento',
            data: pts,
            parsing: false,
            pointRadius: 2.5,
            pointBackgroundColor: pts.map(function (p) { return p.ok ? 'rgba(56, 66, 75, 0.55)' : RED; }),
            pointBorderColor:    pts.map(function (p) { return p.ok ? 'rgba(56, 66, 75, 0.7)'  : RED; })
          }
        ]
      },
      options: {
        parsing: false,
        scales: {
          x: {
            type: 'time', time: { unit: pickTimeUnit(sorted) },
            grid: { color: LINE }, border: { color: LINE }, ticks: { color: INK_MUTE }
          },
          y: {
            title: { display: true, text: 'Airblast — dBL pico (Linear)', color: INK_MUTE },
            min: 40, suggestedMax: 145,
            grid: { color: LINE }, border: { color: LINE }, ticks: { color: INK_MUTE }
          }
        },
        plugins: {
          legend: { position: 'bottom', labels: { color: INK, boxWidth: 14, boxHeight: 2 } },
          tooltip: Object.assign({}, TOOLTIP, {
            callbacks: {
              label: function (c) {
                var p = c.raw;
                if (typeof p.point === 'undefined') return c.dataset.label;
                return [ p.point, 'Airblast: ' + p.y.toFixed(1) + ' dBL', p.ok ? '✓ abaixo do limite NBR' : '× acima do limite NBR' ];
              },
              title: function (items) {
                var iso = items[0].raw.x;
                return iso ? new Date(iso).toLocaleDateString('pt-BR') : '';
              }
            }
          })
        }
      }
    });
  }
  function linePairs(sorted, y) {
    if (!sorted.length) return [];
    return [{ x: sorted[0].event_iso, y: y }, { x: sorted[sorted.length-1].event_iso, y: y }];
  }
  function pickTimeUnit(sorted) {
    if (!sorted.length) return 'month';
    var t0 = new Date(sorted[0].event_iso).getTime();
    var t1 = new Date(sorted[sorted.length-1].event_iso).getTime();
    var days = (t1 - t0) / (1000*60*60*24);
    if (days > 365 * 2) return 'year';
    if (days > 60) return 'month';
    if (days > 5) return 'day';
    return 'hour';
  }

  // --------- 4/5. Evolução mensal PPV / airblast ---------
  function monthlyAvg(records, key) {
    var by = {};
    records.forEach(function (r) {
      if (!r.event_iso || r[key] == null) return;
      var ym = r.event_iso.slice(0, 7);
      (by[ym] = by[ym] || []).push(r[key]);
    });
    var months = Object.keys(by).sort();
    return months.map(function (m) {
      var arr = by[m], sum = arr.reduce(function (s, v) { return s + v; }, 0);
      return { x: m + '-01', y: sum / arr.length, max: Math.max.apply(null, arr) };
    });
  }
  function ppvMonthly(records, curveKey) {
    var sorted = records.slice().filter(function (r) { return r.event_iso; })
      .sort(function (a,b) { return a.event_iso.localeCompare(b.event_iso); });
    var withPpv = sorted.map(function (r) {
      var d = SismoCompliance.dominantAxis(r);
      return Object.assign({}, r, { _ppv: d ? d.ppv : r.pvs_mm_s });
    });
    var series = monthlyAvg(withPpv, '_ppv');

    mount('ch-ppv-month', {
      type: 'line',
      data: {
        datasets: [
          { label: 'PPV médio (mm/s)', data: series.map(function (s) { return { x: s.x, y: s.y }; }),
            borderColor: INK, backgroundColor: INK, borderWidth: 1.6, pointRadius: 2, tension: 0.2, parsing: false },
          { label: 'PPV máx. (mm/s)',  data: series.map(function (s) { return { x: s.x, y: s.max }; }),
            borderColor: RED, borderWidth: 1, borderDash: [3,3], pointRadius: 0, tension: 0, parsing: false }
        ]
      },
      options: {
        parsing: false,
        scales: {
          x: { type: 'time', time: { unit: 'month' }, grid: { color: LINE }, ticks: { color: INK_MUTE } },
          y: { beginAtZero: true, title: { display: true, text: 'PPV (mm/s)', color: INK_MUTE }, grid: { color: LINE }, ticks: { color: INK_MUTE } }
        },
        plugins: {
          legend: { position: 'bottom', labels: { color: INK, boxWidth: 14, boxHeight: 2 } },
          tooltip: TOOLTIP
        }
      }
    });
  }
  function airMonthly(records) {
    var sorted = records.slice().filter(function (r) { return r.event_iso && r.pspl_db != null; })
      .sort(function (a,b) { return a.event_iso.localeCompare(b.event_iso); });
    var series = monthlyAvg(sorted, 'pspl_db');
    mount('ch-air-month', {
      type: 'line',
      data: {
        datasets: [
          { label: 'Airblast médio (dBL)', data: series.map(function (s) { return { x: s.x, y: s.y }; }),
            borderColor: INK, borderWidth: 1.6, pointRadius: 2, tension: 0.2, parsing: false },
          { label: 'Limite NBR 134 dBL', data: series.length ? [{ x: series[0].x, y: 134 }, { x: series[series.length-1].x, y: 134 }] : [],
            borderColor: RED, borderWidth: 1, borderDash: [3,3], pointRadius: 0, parsing: false }
        ]
      },
      options: {
        parsing: false,
        scales: {
          x: { type: 'time', time: { unit: 'month' }, grid: { color: LINE }, ticks: { color: INK_MUTE } },
          y: { title: { display: true, text: 'Airblast (dBL)', color: INK_MUTE }, min: 40, suggestedMax: 145, grid: { color: LINE }, ticks: { color: INK_MUTE } }
        },
        plugins: { legend: { position: 'bottom', labels: { color: INK, boxWidth: 14, boxHeight: 2 } }, tooltip: TOOLTIP }
      }
    });
  }

  // --------- 6. PPV por ponto ---------
  function ppvByPoint(records) {
    var by = {};
    records.forEach(function (r) {
      var d = SismoCompliance.dominantAxis(r);
      var v = d ? d.ppv : r.pvs_mm_s;
      if (v == null) return;
      (by[r.point_name] = by[r.point_name] || []).push(v);
    });
    var names = Object.keys(by);
    var rows = names.map(function (n) {
      var arr = by[n].slice().sort(function (a, b) { return a - b; });
      return { name: n, max: arr[arr.length - 1], p95: percentile(arr, 0.95) };
    }).sort(function (a, b) { return b.max - a.max; });

    mount('ch-ppv-point', {
      type: 'bar',
      data: {
        labels: rows.map(function (r) { return r.name; }),
        datasets: [
          { label: 'PPV máx. (mm/s)', data: rows.map(function (r) { return r.max; }), backgroundColor: RED, borderRadius: 1 },
          { label: 'PPV p95 (mm/s)',  data: rows.map(function (r) { return r.p95; }), backgroundColor: INK, borderRadius: 1 }
        ]
      },
      options: {
        indexAxis: 'y',
        scales: {
          x: { beginAtZero: true, title: { display: true, text: 'PPV (mm/s)', color: INK_MUTE }, grid: { color: LINE }, ticks: { color: INK_MUTE } },
          y: { grid: { display: false }, ticks: { color: INK, font: { size: 10 } } }
        },
        plugins: { legend: { position: 'bottom', labels: { color: INK, boxWidth: 14, boxHeight: 2 } }, tooltip: TOOLTIP }
      }
    });
  }
  function percentile(sortedArr, q) {
    if (!sortedArr.length) return 0;
    var i = (sortedArr.length - 1) * q;
    var lo = Math.floor(i), hi = Math.ceil(i);
    if (lo === hi) return sortedArr[lo];
    return sortedArr[lo] + (sortedArr[hi] - sortedArr[lo]) * (i - lo);
  }

  // --------- 7. Distribuição de frequências ---------
  function freqDist(records, curveKey) {
    var bins = [
      { label: '< 4 Hz',  lo: 0,  hi: 4 },
      { label: '4–15 Hz', lo: 4,  hi: 15 },
      { label: '15–40 Hz',lo: 15, hi: 40 },
      { label: '> 40 Hz', lo: 40, hi: Infinity }
    ];
    var ok = new Array(bins.length).fill(0);
    var bad = new Array(bins.length).fill(0);
    records.forEach(function (r) {
      var e = SismoCompliance.evaluate(r, curveKey);
      if (e.freq_ref == null) return;
      for (var i = 0; i < bins.length; i++) {
        if (e.freq_ref >= bins[i].lo && e.freq_ref < bins[i].hi) {
          if (e.conforme === false) bad[i]++; else ok[i]++;
          break;
        }
      }
    });
    mount('ch-freq-dist', {
      type: 'bar',
      data: {
        labels: bins.map(function (b) { return b.label; }),
        datasets: [
          { label: 'Abaixo do limite', data: ok,  backgroundColor: INK, borderRadius: 1 },
          { label: 'Acima do limite',  data: bad, backgroundColor: RED, borderRadius: 1 }
        ]
      },
      options: {
        scales: {
          x: { grid: { display: false }, ticks: { color: INK_MUTE } },
          y: { beginAtZero: true, title: { display: true, text: 'N° de eventos', color: INK_MUTE }, grid: { color: LINE }, ticks: { color: INK_MUTE } }
        },
        plugins: { legend: { position: 'bottom', labels: { color: INK, boxWidth: 14, boxHeight: 2 } }, tooltip: TOOLTIP }
      }
    });
  }

  // --------- 8. Distância escalada × PPV ---------
  function scaledDistance(records) {
    var pts = records.map(function (r) {
      var d = SismoCompliance.dominantAxis(r);
      var y = d ? d.ppv : r.pvs_mm_s;
      var x = r.scaled_distance;
      if (!x || !y || x <= 0 || y <= 0) return null;
      return { x: x, y: y, point: r.point_name };
    }).filter(Boolean);

    // Ajuste v = a * DE^b via mínimos quadrados em log-log.
    var fit = fitPowerLaw(pts);
    var line = [];
    if (fit) {
      for (var lx = Math.log10(Math.max(0.5, fit.xMin)); lx <= Math.log10(fit.xMax); lx += 0.05) {
        var x = Math.pow(10, lx);
        line.push({ x: x, y: fit.a * Math.pow(x, fit.b) });
      }
    }
    var sub = document.getElementById('sub-de');
    if (sub && fit) {
      sub.textContent = 'DE = R / √Q (m/√kg) · ' + pts.length + ' eventos · ajuste: v = ' + fit.a.toFixed(2) + '·DE^' + fit.b.toFixed(2) + ' (R² = ' + fit.r2.toFixed(2) + ')';
    } else if (sub) {
      sub.textContent = 'DE = R / √Q (m/√kg) · sem eventos suficientes para ajuste';
    }

    mount('ch-de', {
      type: 'scatter',
      data: {
        datasets: [
          { label: 'Eventos', data: pts, parsing: false,
            backgroundColor: 'rgba(56, 66, 75, 0.55)', borderColor: 'rgba(56, 66, 75, 0.7)', pointRadius: 2.5 },
          fit ? { label: 'Regressão v = a·DE^b', type: 'line', data: line, parsing: false,
            borderColor: RED, borderWidth: 1.4, pointRadius: 0 } : null
        ].filter(Boolean)
      },
      options: {
        parsing: false,
        scales: {
          x: { type: 'logarithmic', title: { display: true, text: 'Distância escalada DE (m/√kg)', color: INK_MUTE }, grid: { color: LINE }, ticks: { color: INK_MUTE } },
          y: { type: 'logarithmic', title: { display: true, text: 'PPV (mm/s)', color: INK_MUTE }, grid: { color: LINE }, ticks: { color: INK_MUTE } }
        },
        plugins: { legend: { position: 'bottom', labels: { color: INK, boxWidth: 14, boxHeight: 2 } }, tooltip: TOOLTIP }
      }
    });
  }
  function fitPowerLaw(pts) {
    if (pts.length < 3) return null;
    var xs = [], ys = [], xMin = Infinity, xMax = -Infinity;
    pts.forEach(function (p) {
      xs.push(Math.log10(p.x));
      ys.push(Math.log10(p.y));
      if (p.x < xMin) xMin = p.x;
      if (p.x > xMax) xMax = p.x;
    });
    var n = xs.length;
    var sx = 0, sy = 0, sxx = 0, sxy = 0;
    for (var i = 0; i < n; i++) { sx += xs[i]; sy += ys[i]; sxx += xs[i]*xs[i]; sxy += xs[i]*ys[i]; }
    var b = (n * sxy - sx * sy) / (n * sxx - sx * sx);
    var loga = (sy - b * sx) / n;
    var a = Math.pow(10, loga);
    // R²
    var meanY = sy / n, ssTot = 0, ssRes = 0;
    for (var j = 0; j < n; j++) {
      var pred = loga + b * xs[j];
      ssRes += (ys[j] - pred) * (ys[j] - pred);
      ssTot += (ys[j] - meanY) * (ys[j] - meanY);
    }
    var r2 = ssTot > 0 ? 1 - ssRes / ssTot : 0;
    return { a: a, b: b, r2: r2, xMin: xMin, xMax: xMax };
  }

  // --------- 9. Séries por eixo ---------
  function axisSeries(records) {
    var sorted = records.slice().filter(function (r) { return r.event_iso; })
      .sort(function (a, b) { return a.event_iso.localeCompare(b.event_iso); });

    function mk(id, valueKey, color, label) {
      var data = sorted.map(function (r) {
        return r[valueKey] == null ? null : { x: r.event_iso, y: r[valueKey] };
      }).filter(Boolean);
      mount(id, {
        type: 'line',
        data: { datasets: [{
          label: label, data: data, parsing: false,
          borderColor: color, backgroundColor: color + '22',
          borderWidth: 1.2, pointRadius: 0, fill: true, tension: 0.2
        }] },
        options: {
          parsing: false,
          scales: {
            x: { type: 'time', time: { unit: pickTimeUnit(sorted) }, grid: { color: LINE }, ticks: { color: INK_MUTE, maxRotation: 0 } },
            y: { beginAtZero: true, grid: { color: LINE }, ticks: { color: INK_MUTE } }
          },
          plugins: { legend: { display: false }, tooltip: TOOLTIP }
        }
      });
    }

    mk('ch-ax-vL', 'long_ppv_mm_s', BLUE,   'Long PPV (mm/s)');
    mk('ch-ax-fL', 'long_freq_hz',  BLUE,   'Long freq (Hz)');
    mk('ch-ax-vV', 'vert_ppv_mm_s', RED,    'Vert PPV (mm/s)');
    mk('ch-ax-fV', 'vert_freq_hz',  RED,    'Vert freq (Hz)');
    mk('ch-ax-vT', 'tran_ppv_mm_s', VIOLET, 'Tran PPV (mm/s)');
    mk('ch-ax-fT', 'tran_freq_hz',  VIOLET, 'Tran freq (Hz)');
  }

  window.SismoCharts = {
    renderAll: function (records, curveKey) {
      velocityFrequency(records, curveKey);
      ppvByEvent(records, curveKey);
      airblastByEvent(records);
      ppvMonthly(records, curveKey);
      airMonthly(records);
      ppvByPoint(records);
      freqDist(records, curveKey);
      scaledDistance(records);
      axisSeries(records);
    },
    destroyAll: function () { Object.keys(CHARTS).forEach(destroy); }
  };
})();
