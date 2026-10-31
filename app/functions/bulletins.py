import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

from tropycal.utils import get_basin

from app.functions.unit import present_observation

STANDARD_HOURS = {'0000', '0600', '1200', '1800'}
ACTIVE_WINDOW = timedelta(hours=12)
NHC_INDEX = 'https://ftp.nhc.noaa.gov/atcf/btk/'
UCAR_INDEX = 'https://hurricanes.ral.ucar.edu/repository/data/bdecks_open/{year}/'


def _read(url, timeout):
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return response.read().decode('utf-8', 'replace')


def _filenames(html, pattern):
    return sorted(set(re.findall(pattern, html)))


def _coordinate(token):
    if not token:
        return None
    hemisphere = token[-1]
    if hemisphere not in 'NSEW':
        return None
    value = float(token[:-1]) * 0.1
    if hemisphere in ('S', 'W'):
        value = -value
    return round(value, 1)


def latest_fix(text):
    """Dernière position synoptique d'un bulletin ATCF."""
    latest = None
    for raw in text.splitlines():
        fields = raw.replace(' ', '').split(',')
        if len(fields) < 28 or len(fields[2]) < 10 or not fields[2][:10].isdigit():
            continue
        when = datetime.strptime(fields[2][:10], '%Y%m%d%H')
        if when.strftime('%H%M') not in STANDARD_HOURS:
            continue
        if latest and when - latest['time'] > timedelta(days=30):
            latest = None

        wind = int(fields[8]) if fields[8].lstrip('-').isdigit() else None
        pressure = int(fields[9]) if fields[9].lstrip('-').isdigit() else None
        if wind is not None and (wind < 10 or wind > 250):
            wind = None
        if pressure is not None and (pressure < 800 or pressure > 1040):
            pressure = None

        latest = {
            'time': when,
            'lat': _coordinate(fields[6]),
            'lon': _coordinate(fields[7]),
            'vmax': wind,
            'mslp': pressure,
            'name': fields[27] or 'Sans nom',
        }
    return latest


def _storm_id(filename):
    return filename.split('.dat')[0][1:].upper()


def _origin_basin(storm_id):
    if storm_id.startswith('AL'):
        return 'north_atlantic'
    if storm_id[:2] in ('EP', 'CP') or storm_id[0] in ('E', 'C'):
        return 'east_pacific'
    if storm_id.startswith('IO') or storm_id[0] == 'I':
        return 'north_indian'
    if storm_id[0] == 'S':
        return ''
    return 'west_pacific'


def _display_name(storm_id, fix):
    if len(storm_id) >= 3 and storm_id[2] == '9':
        letters = {'C': 'C', 'E': 'E', 'W': 'W', 'I': 'I', 'S': 'S'}
        return storm_id[2:4] + letters.get(storm_id[0], 'L')
    return fix['name'] or 'Sans nom'


def storm_from_bulletin(filename, text, source, now):
    storm_id = _storm_id(filename)
    if source == 'ucar' and storm_id[0] in ('E', 'C') and storm_id[2] == '9':
        return None

    fix = latest_fix(text)
    if fix is None or fix['lat'] is None or fix['lon'] is None or fix['vmax'] is None:
        return None
    if now - fix['time'] >= ACTIVE_WINDOW:
        return None

    basin = get_basin(fix['lat'], fix['lon'], _origin_basin(storm_id))
    presented = present_observation(fix['vmax'], fix['mslp'] or 0, basin)
    return {
        'name': _display_name(storm_id, fix),
        'idCyclone': storm_id,
        'vmax': presented['vmax'],
        'mslp': presented['mslp'],
        'lat': fix['lat'],
        'lon': fix['lon'],
        'classification': presented['classification'],
        'basin': basin,
        'is_invest': storm_id[2] == '9',
        'source': source,
        'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }


def fetch_active_storms(now=None, timeout=20):
    """Lit NHC et UCAR en parallèle et ne garde que les cyclones des 12 dernières heures."""
    now = now or datetime.now(timezone.utc).replace(tzinfo=None)
    year = now.year
    nhc_html = _read(NHC_INDEX, timeout)
    ucar_html = _read(UCAR_INDEX.format(year=year), timeout)
    nhc_files = _filenames(nhc_html, rf'b[aec][lp][012349]\d{year}\.dat')
    ucar_files = _filenames(ucar_html, rf'b[iswec][ohp][012349]\d{year}\.dat')
    if not nhc_files and not ucar_files:
        raise RuntimeError('Aucun bulletin trouvé dans les index')

    jobs = [(name, f'{NHC_INDEX}{name}', 'nhc') for name in nhc_files]
    jobs += [
        (name, UCAR_INDEX.format(year=year) + name, 'ucar')
        for name in ucar_files
    ]

    storms = {}
    readable = 0
    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = {
            executor.submit(_read, url, timeout): (filename, source)
            for filename, url, source in jobs
        }
        for future in futures:
            filename, source = futures[future]
            try:
                text = future.result()
            except Exception as error:
                print(f"❌ Bulletin {filename} illisible : {error}")
                continue
            readable += 1
            storm = storm_from_bulletin(filename, text, source, now)
            if storm is None:
                continue
            if source == 'ucar' and storm['idCyclone'] in storms:
                continue
            storms[storm['idCyclone']] = storm

    if jobs and readable == 0:
        raise RuntimeError("Aucun bulletin n'a pu être lu")
    return list(storms.values())
