/* Parser para CSVs ISEE (Micromate / Instantel).
 * Espelha src/parser.py do pipeline Python: lê o cabeçalho chave→valor
 * até encontrar a tabela de onda (linhas com "Tran, Vert, Long, MicL")
 * e extrai os campos técnicos. Roda 100% no navegador.
 */
(function () {
  'use strict';

  function stripAccents(s) {
    return s.normalize('NFD').replace(/[̀-ͯ]/g, '');
  }
  function normKey(s) {
    return stripAccents(String(s || '')).toLowerCase().replace(/[^a-z0-9]+/g, '');
  }
  function parseFloatBR(v) {
    if (v == null) return null;
    var txt = String(v).replace(/ /g, ' ').trim();
    if (!txt) return null;
    var m = txt.match(/[-+]?\d+(?:[.,]\d+)?/);
    if (!m) return null;
    var n = parseFloat(m[0].replace(',', '.'));
    return isNaN(n) ? null : n;
  }
  function parseScaledDistance(value) {
    var res = { scaled_distance: null, distance_m: null, charge_kg: null };
    if (!value) return res;
    var nums = String(value).match(/[-+]?\d+(?:[.,]\d+)?/g);
    if (!nums) return res;
    nums = nums.map(function (n) { return parseFloat(n.replace(',', '.')); });
    if (nums.length >= 1) res.scaled_distance = nums[0];
    if (nums.length >= 2) res.distance_m = nums[1];
    if (nums.length >= 3) res.charge_kg = nums[2];
    return res;
  }

  function parseRawCsv(text) {
    // Papa parses quoted CSV correctly; header is a series of 2-column rows.
    var out = Papa.parse(text, { skipEmptyLines: true });
    return out.data || [];
  }

  function readHeader(rows) {
    var meta = {};
    var titleNotes = {}, titleStrings = {};
    for (var i = 0; i < rows.length; i++) {
      var row = rows[i].map(function (c) { return (c == null ? '' : String(c)).trim(); });
      if (row.length === 0) continue;
      if (row.length >= 4 &&
          normKey(row[0]) === 'tran' &&
          normKey(row[1]) === 'vert' &&
          normKey(row[2]) === 'long' &&
          normKey(row[3]) === 'micl') {
        break;
      }
      if (row.length >= 2) {
        var key = row[0], val = row[1];
        if (key) {
          meta[key] = val;
          var nk = normKey(key);
          var mNote = nk.match(/^titlenote(\d+)$/);
          var mStr  = nk.match(/^titlestring(\d+)$/);
          if (mNote) titleNotes[mNote[1]] = val;
          if (mStr) titleStrings[mStr[1]] = val;
        }
      }
    }
    Object.keys(titleNotes).forEach(function (idx) {
      var note = titleNotes[idx];
      var val = titleStrings[idx] || '';
      if (note) meta['Title::' + note] = val;
    });
    return meta;
  }

  function parseSismoCsv(fileName, text) {
    var rows = parseRawCsv(text);
    var meta = readHeader(rows);
    var norm = {};
    Object.keys(meta).forEach(function (k) { norm[normKey(k)] = meta[k]; });

    var location = norm['titlelocation'] || meta['Title::Location'] || meta['TitleString1'] || fileName.replace(/\.[^.]+$/, '');
    var client   = norm['titleclient']   || meta['Title::Client']   || meta['TitleString2'] || null;
    var company  = norm['titlecompany']  || meta['Title::Company']  || meta['TitleString3'] || null;

    var scaled = parseScaledDistance(meta['ScaledDistance'] || '');
    var gpsDist = parseFloatBR(meta['GpsDistance']);
    if (gpsDist == null) gpsDist = scaled.distance_m;

    var eventDate = meta['EventDate'] || null;
    var eventTime = meta['EventTime'] || null;

    return {
      source_file: fileName,
      event_date: eventDate,
      event_time: eventTime,
      event_iso: buildIso(eventDate, eventTime),
      point_name: String(location).trim() || fileName.replace(/\.[^.]+$/, ''),
      client: client,
      company: company,
      serial_number: meta['SerialNumber'] || null,
      calibration: meta['Calibration'] || null,
      gps_distance_m: gpsDist,
      scaled_distance: scaled.scaled_distance,
      charge_kg: scaled.charge_kg,
      pspl_db: parseFloatBR(meta['MicPSPL']),
      mic_freq_hz: parseFloatBR(meta['MicZCFreq']),
      pvs_mm_s: parseFloatBR(meta['PeakVectorSum']),
      tran_ppv_mm_s: parseFloatBR(meta['TranPPV']),
      vert_ppv_mm_s: parseFloatBR(meta['VertPPV']),
      long_ppv_mm_s: parseFloatBR(meta['LongPPV']),
      tran_freq_hz: parseFloatBR(meta['TranZCFreq']),
      vert_freq_hz: parseFloatBR(meta['VertZCFreq']),
      long_freq_hz: parseFloatBR(meta['LongZCFreq']),
      mic_test_result: meta['MicTestResults'] || null,
      tran_test_result: meta['TranTestResults'] || null,
      vert_test_result: meta['VertTestResults'] || null,
      long_test_result: meta['LongTestResults'] || null
    };
  }

  function buildIso(date, time) {
    if (!date) return null;
    // Aceita formatos "2026-06-30" ou "30/06/2026" ou "June 30, 2026"
    var iso;
    var m1 = /^(\d{4})-(\d{2})-(\d{2})$/.exec(date);
    var m2 = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec(date);
    if (m1) iso = m1[1] + '-' + m1[2] + '-' + m1[3];
    else if (m2) iso = m2[3] + '-' + m2[2] + '-' + m2[1];
    else {
      var d = new Date(date);
      if (!isNaN(d.getTime())) {
        iso = d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0');
      } else {
        return null;
      }
    }
    if (time && /^\d{2}:\d{2}(:\d{2})?$/.test(time)) {
      iso += 'T' + (time.length === 5 ? time + ':00' : time);
    } else {
      iso += 'T00:00:00';
    }
    return iso;
  }

  window.SismoParser = {
    parseSismoCsv: parseSismoCsv,
    normKey: normKey,
    parseFloatBR: parseFloatBR
  };
})();
