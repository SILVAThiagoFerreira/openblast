from __future__ import annotations

import csv
import re
import unicodedata
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional


def _strip_accents(value: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', value) if unicodedata.category(c) != 'Mn')


def norm_key(value: str) -> str:
    return re.sub(r'[^a-z0-9]+', '', _strip_accents(str(value)).lower())


def parse_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    txt = str(value).strip().replace('\u00a0', ' ')
    if not txt:
        return None
    # Captura o primeiro número em formatos 1.234,56 ou 1234.56.
    m = re.search(r'[-+]?\d+(?:[\.,]\d+)?', txt)
    if not m:
        return None
    number = m.group(0).replace(',', '.')
    try:
        return float(number)
    except ValueError:
        return None


def parse_scaled_distance(value: str) -> Dict[str, Optional[float]]:
    """Extrai SD, distância e carga de textos como '4586.9 (1450.5 m, 0.1 kg)'."""
    result = {"scaled_distance": None, "distance_m": None, "charge_kg": None}
    if not value:
        return result
    nums = re.findall(r'[-+]?\d+(?:[\.,]\d+)?', str(value))
    nums = [float(n.replace(',', '.')) for n in nums]
    if len(nums) >= 1:
        result["scaled_distance"] = nums[0]
    if len(nums) >= 2:
        result["distance_m"] = nums[1]
    if len(nums) >= 3:
        result["charge_kg"] = nums[2]
    return result


def find_input_csvs(input_path: str | Path) -> List[Path]:
    path = Path(input_path)
    if path.is_file():
        return [path]
    if not path.exists():
        raise FileNotFoundError(f"Entrada não encontrada: {path}")
    files = sorted([p for p in path.rglob('*') if p.suffix.lower() == '.csv'])
    if not files:
        raise FileNotFoundError(f"Nenhum CSV encontrado em: {path}")
    return files


@dataclass
class SismoRecord:
    source_file: str
    event_date: Optional[str]
    event_time: Optional[str]
    point_name: str
    client: Optional[str]
    company: Optional[str]
    serial_number: Optional[str]
    calibration: Optional[str]
    gps_distance_m: Optional[float]
    scaled_distance: Optional[float]
    charge_kg: Optional[float]
    pspl_db: Optional[float]
    mic_freq_hz: Optional[float]
    pvs_mm_s: Optional[float]
    tran_ppv_mm_s: Optional[float]
    vert_ppv_mm_s: Optional[float]
    long_ppv_mm_s: Optional[float]
    tran_freq_hz: Optional[float]
    vert_freq_hz: Optional[float]
    long_freq_hz: Optional[float]
    tran_time_peak_s: Optional[float]
    vert_time_peak_s: Optional[float]
    long_time_peak_s: Optional[float]
    mic_time_peak_s: Optional[float]
    mic_test_result: Optional[str]
    tran_test_result: Optional[str]
    vert_test_result: Optional[str]
    long_test_result: Optional[str]
    metadata: Dict[str, str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def read_header_metadata(path: str | Path) -> Dict[str, str]:
    """Lê apenas o cabeçalho do CSV até encontrar a tabela de onda (Tran, Vert, Long, MicL)."""
    metadata: Dict[str, str] = {}
    path = Path(path)
    with path.open('r', encoding='utf-8-sig', newline='', errors='replace') as f:
        reader = csv.reader(f)
        title_notes: Dict[str, str] = {}
        title_strings: Dict[str, str] = {}
        for row in reader:
            if not row:
                continue
            compact = [c.strip() for c in row]
            if len(compact) >= 4 and [norm_key(c) for c in compact[:4]] == ['tran', 'vert', 'long', 'micl']:
                break
            if len(compact) >= 2:
                key, value = compact[0], compact[1]
                metadata[key] = value
                nk = norm_key(key)
                note_match = re.fullmatch(r'titlenote(\d+)', nk)
                string_match = re.fullmatch(r'titlestring(\d+)', nk)
                if note_match:
                    title_notes[note_match.group(1)] = value
                if string_match:
                    title_strings[string_match.group(1)] = value
        for idx, note in title_notes.items():
            value = title_strings.get(idx, '')
            if note:
                metadata[f'Title::{note}'] = value
    return metadata


def parse_sismo_csv(path: str | Path) -> SismoRecord:
    path = Path(path)
    meta = read_header_metadata(path)
    normalized = {norm_key(k): v for k, v in meta.items()}

    location = normalized.get('titlelocation') or meta.get('Title::Location') or meta.get('TitleString1') or path.stem
    client = normalized.get('titleclient') or meta.get('Title::Client') or meta.get('TitleString2')
    company = normalized.get('titlecompany') or meta.get('Title::Company') or meta.get('TitleString3')

    scaled = parse_scaled_distance(meta.get('ScaledDistance', ''))
    gps_distance = parse_float(meta.get('GpsDistance')) or scaled.get('distance_m')

    return SismoRecord(
        source_file=path.name,
        event_date=meta.get('EventDate'),
        event_time=meta.get('EventTime'),
        point_name=str(location).strip() or path.stem,
        client=client,
        company=company,
        serial_number=meta.get('SerialNumber'),
        calibration=meta.get('Calibration'),
        gps_distance_m=gps_distance,
        scaled_distance=scaled.get('scaled_distance'),
        charge_kg=scaled.get('charge_kg'),
        pspl_db=parse_float(meta.get('MicPSPL')),
        mic_freq_hz=parse_float(meta.get('MicZCFreq')),
        pvs_mm_s=parse_float(meta.get('PeakVectorSum')),
        tran_ppv_mm_s=parse_float(meta.get('TranPPV')),
        vert_ppv_mm_s=parse_float(meta.get('VertPPV')),
        long_ppv_mm_s=parse_float(meta.get('LongPPV')),
        tran_freq_hz=parse_float(meta.get('TranZCFreq')),
        vert_freq_hz=parse_float(meta.get('VertZCFreq')),
        long_freq_hz=parse_float(meta.get('LongZCFreq')),
        tran_time_peak_s=parse_float(meta.get('TranTimeofPeak')),
        vert_time_peak_s=parse_float(meta.get('VertTimeofPeak')),
        long_time_peak_s=parse_float(meta.get('LongTimeofPeak')),
        mic_time_peak_s=parse_float(meta.get('MicTimeofPeak')),
        mic_test_result=meta.get('MicTestResults'),
        tran_test_result=meta.get('TranTestResults'),
        vert_test_result=meta.get('VertTestResults'),
        long_test_result=meta.get('LongTestResults'),
        metadata=meta,
    )


def parse_many(input_path: str | Path) -> List[SismoRecord]:
    return [parse_sismo_csv(p) for p in find_input_csvs(input_path)]
