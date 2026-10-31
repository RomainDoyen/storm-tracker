import threading
import time
from datetime import datetime

from dotenv import load_dotenv

from app.db import database_available, list_cyclones, replace_cyclones
from app.functions.bulletins import fetch_active_storms
from app.functions.sync import cached_payload

load_dotenv()

UPDATE_INTERVAL = 1800
CACHE_DURATION = 900

data_cache = {
    'last_update': None,
    'data': None,
    'is_updating': False,
}

_update_lock = threading.Lock()
_last_fetch = {'storms': None}
_updater_started = False


def is_cache_valid():
    return get_cached_data() is not None


def get_cached_data():
    return cached_payload(
        data_cache['data'],
        data_cache['last_update'],
        datetime.now(),
        CACHE_DURATION,
    )


def update_in_progress():
    return data_cache['is_updating']


def update_cache(new_data):
    data_cache['data'] = new_data
    data_cache['last_update'] = datetime.now()
    print(f"💾 Cache mis à jour avec {len(new_data)} cyclones")


def _fetch_current_storms():
    print("🔄 Récupération des cyclones actifs...")
    start_time = time.time()
    storms = fetch_active_storms()
    elapsed = time.time() - start_time
    print(f"⏱️ Bulletins lus en {elapsed:.2f}s - {len(storms)} cyclones")
    for storm in storms:
        print(f"✅ Cyclone {storm['idCyclone']} traité")
    return storms


def _fetch_and_store():
    data_cache['is_updating'] = True
    try:
        storms = _fetch_current_storms()
        if database_available():
            replace_cyclones(storms)
        else:
            print("⚠️ Neon non disponible - les cyclones restent dans le cache du processus")
        update_cache(storms)
        print(f"✅ Mise à jour terminée - {len(storms)} cyclones actifs.")
        return storms
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour: {e}")
        return None
    finally:
        data_cache['is_updating'] = False


def run_live_update():
    """Lance une mise à jour, ou attend celle déjà en cours, puis retourne les cyclones."""
    if not _update_lock.acquire(blocking=False):
        with _update_lock:
            return _last_fetch['storms']
    try:
        storms = _fetch_and_store()
        _last_fetch['storms'] = storms
        return storms
    finally:
        _update_lock.release()


def initialize_cache_from_database():
    """Sert les dernières fiches connues si la récupération en direct échoue."""
    try:
        if not database_available():
            print("⚠️ Neon non disponible pour l'initialisation du cache")
            return
        print("🔄 Initialisation du cache avec les cyclones déjà en base...")
        existing_cyclones = list_cyclones()
        if existing_cyclones:
            update_cache(existing_cyclones)
            print(f"✅ Cache initialisé avec {len(existing_cyclones)} cyclones existants")
        else:
            print("⚠️ Aucune donnée existante dans Neon")
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation du cache: {type(e).__name__}")


def update_cyclones_data():
    """Met à jour les cyclones au démarrage, puis toutes les 30 minutes."""
    data_cache['is_updating'] = True
    initialize_cache_from_database()
    while True:
        run_live_update()
        time.sleep(UPDATE_INTERVAL)


def reset_after_fork():
    """Le fil lancé avant le fork de Gunicorn ne tourne plus dans le worker."""
    global _updater_started
    _updater_started = False
    data_cache['is_updating'] = False
    data_cache['data'] = None
    data_cache['last_update'] = None


def start_background_updates():
    global _updater_started
    if _updater_started:
        return
    _updater_started = True
    thread = threading.Thread(target=update_cyclones_data, daemon=True)
    thread.start()


def force_update_cyclones_data():
    """Compatibilité avec l'ancien point d'entrée manuel."""
    return run_live_update()
