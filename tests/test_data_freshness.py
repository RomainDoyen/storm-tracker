import importlib.util
import sys
import types
import unittest
from datetime import datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(qualname, relative_path):
    if 'app' not in sys.modules:
        app_mod = types.ModuleType('app')
        app_mod.__path__ = [str(ROOT / 'app')]
        sys.modules['app'] = app_mod
    if 'app.functions' not in sys.modules:
        functions_mod = types.ModuleType('app.functions')
        functions_mod.__path__ = [str(ROOT / 'app' / 'functions')]
        sys.modules['app.functions'] = functions_mod

    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(qualname, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[qualname] = module
    spec.loader.exec_module(module)
    return module


classification = load_module(
    'app.functions.classification',
    'app/functions/classification.py',
)
unit = load_module('app.functions.unit', 'app/functions/unit.py')
sync = load_module('app.functions.sync', 'app/functions/sync.py')
bulletins = load_module('app.functions.bulletins', 'app/functions/bulletins.py')


class MemoryStore:
    def __init__(self, storms):
        self.storms = {storm['idCyclone']: storm for storm in storms}

    def list_ids(self):
        return list(self.storms)

    def save(self, storm):
        self.storms[storm['idCyclone']] = storm

    def delete(self, storm_id):
        del self.storms[storm_id]


class ObservationTests(unittest.TestCase):
    def test_pressure_is_expressed_in_bar(self):
        self.assertAlmostEqual(unit.hpa_to_bar(1003), 1.003, places=3)

    def test_classification_uses_knots_while_wind_is_shown_in_kmh(self):
        observation = unit.present_observation(45, 1003, 'north_atlantic')

        self.assertEqual(observation['classification'], 'Tempête tropicale')
        self.assertAlmostEqual(observation['vmax'], 83.34, places=2)
        self.assertAlmostEqual(observation['mslp'], 1.003, places=3)


class SyncTests(unittest.TestCase):
    def test_successful_fetch_drops_storms_that_ended(self):
        store = MemoryStore([
            {'idCyclone': 'AL072025', 'name': 'GABRIELLE'},
        ])

        updated = sync.sync_cyclone_store(store, [
            {'idCyclone': 'WP302026', 'name': 'IN-FA'},
        ], True)

        self.assertTrue(updated)
        self.assertEqual(set(store.storms), {'WP302026'})

    def test_successful_fetch_with_no_active_storm_clears_the_store(self):
        store = MemoryStore([
            {'idCyclone': 'AL072025', 'name': 'GABRIELLE'},
        ])

        sync.sync_cyclone_store(store, [], True)

        self.assertEqual(store.storms, {})

    def test_failed_fetch_keeps_the_previous_storms(self):
        store = MemoryStore([
            {'idCyclone': 'AL072025', 'name': 'GABRIELLE'},
        ])

        updated = sync.sync_cyclone_store(store, [], False)

        self.assertFalse(updated)
        self.assertIn('AL072025', store.storms)

    def test_empty_live_result_stays_in_cache(self):
        now = datetime(2026, 10, 31, 14, 30)
        cached = sync.cached_payload([], now, now, 900)

        self.assertEqual(cached, [])


class BulletinTests(unittest.TestCase):
    def test_latest_fix_reads_in_fa_position(self):
        text = (
            "WP, 30, 2026103106,   , BEST,   0, 222N, 1429E, 115,  948, XX,  34, NEQ,  145,  105,  100,  125, "
            "1011,  240,  22,   0,   0,   W,   0,   X, 330,  10,      IN-FA, D\n"
        )
        fix = bulletins.latest_fix(text)
        self.assertEqual(fix['name'], 'IN-FA')
        self.assertEqual(fix['vmax'], 115)
        self.assertEqual(fix['mslp'], 948)
        self.assertAlmostEqual(fix['lat'], 22.2)
        self.assertAlmostEqual(fix['lon'], 142.9)

    def test_active_typhoon_is_kept_and_classified_from_knots(self):
        text = (
            "WP, 30, 2026103106,   , BEST,   0, 222N, 1429E, 115,  948, XX,  34, NEQ,  145,  105,  100,  125, "
            "1011,  240,  22,   0,   0,   W,   0,   X, 330,  10,      IN-FA, D\n"
        )
        storm = bulletins.storm_from_bulletin(
            'bwp302026.dat',
            text,
            'ucar',
            datetime(2026, 10, 31, 14, 0),
        )
        self.assertEqual(storm['idCyclone'], 'WP302026')
        self.assertEqual(storm['name'], 'IN-FA')
        self.assertEqual(storm['classification'], 'Typhon')
        self.assertAlmostEqual(storm['vmax'], 212.98, places=2)
        self.assertAlmostEqual(storm['mslp'], 0.948, places=3)
        self.assertEqual(storm['basin'], 'west_pacific')

    def test_old_storm_is_ignored(self):
        text = (
            "AL, 07, 2025092018,   , BEST,   0, 250N,  550W,  45, 1003, TS,  34, NEQ,    0,    0,    0,    0, "
            "1010,  180,  10,   0,   0,   W,   0,   X,  40,   0, GABRIELLE, D\n"
        )
        storm = bulletins.storm_from_bulletin(
            'bal072025.dat',
            text,
            'nhc',
            datetime(2026, 10, 31, 14, 0),
        )
        self.assertIsNone(storm)


if __name__ == '__main__':
    unittest.main()
