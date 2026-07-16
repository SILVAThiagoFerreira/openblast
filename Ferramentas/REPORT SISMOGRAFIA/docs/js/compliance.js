/* Conformidade e curvas de referência.
 * Espelha src/compliance.py: interpolação linear em curvas PPV × frequência.
 */
(function () {
  'use strict';

  var CURVES = {
    // NBR 9653:2018 — curva única (limite legal)
    'nbr9653': [
      [0, 15], [4, 15], [15, 20], [40, 50], [250, 50]
    ],
    // DIN 4150-3 · Linha 2 — residenciais
    'din4150-2': [
      [0, 5], [10, 5], [50, 15], [100, 20], [250, 20]
    ],
    // DIN 4150-3 · Linha 3 — sensível / construções especiais
    'din4150-3': [
      [0, 3], [10, 3], [50, 8], [100, 10], [250, 10]
    ],
    // USBM RI 8507 (modern homes) — patamar simplificado
    'usbm': [
      [0, 12.5], [4, 12.5], [12, 19], [40, 50], [250, 50]
    ]
  };

  function interpolateLimit(freq, curve) {
    if (freq == null || !curve || !curve.length) return null;
    var pts = curve.slice().sort(function (a, b) { return a[0] - b[0]; });
    if (freq <= pts[0][0]) return pts[0][1];
    for (var i = 0; i < pts.length - 1; i++) {
      var p0 = pts[i], p1 = pts[i+1];
      if (p0[0] <= freq && freq <= p1[0]) {
        if (p1[0] === p0[0]) return p1[1];
        var t = (freq - p0[0]) / (p1[0] - p0[0]);
        return p0[1] + t * (p1[1] - p0[1]);
      }
    }
    return pts[pts.length - 1][1];
  }

  // Ponto "dominante" do evento = eixo cujo PPV é o maior.
  function dominantAxis(rec) {
    var axes = [
      { axis: 'Long', ppv: rec.long_ppv_mm_s, freq: rec.long_freq_hz },
      { axis: 'Vert', ppv: rec.vert_ppv_mm_s, freq: rec.vert_freq_hz },
      { axis: 'Tran', ppv: rec.tran_ppv_mm_s, freq: rec.tran_freq_hz }
    ];
    var best = null;
    axes.forEach(function (a) {
      if (a.ppv == null) return;
      if (!best || a.ppv > best.ppv) best = a;
    });
    return best; // { axis, ppv, freq } | null
  }

  function evaluate(rec, curveKey) {
    var curve = CURVES[curveKey] || CURVES['nbr9653'];
    var dom = dominantAxis(rec);
    var ppv = dom ? dom.ppv : (rec.pvs_mm_s != null ? rec.pvs_mm_s : null);
    var freq = dom ? dom.freq : null;
    var limit = freq != null ? interpolateLimit(freq, curve) : null;
    var conforme = (ppv == null || limit == null) ? null : ppv <= limit;
    return {
      ppv_ref: ppv,           // usado nos gráficos "PPV por evento"
      freq_ref: freq,
      dominant_axis: dom ? dom.axis : null,
      limit: limit,
      conforme: conforme
    };
  }

  window.SismoCompliance = {
    CURVES: CURVES,
    interpolateLimit: interpolateLimit,
    evaluate: evaluate,
    dominantAxis: dominantAxis
  };
})();
