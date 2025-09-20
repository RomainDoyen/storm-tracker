import os
import time
import ssl
import certifi
import numpy as np
import threading
from datetime import datetime, timedelta
from dotenv import load_dotenv
from tropycal import realtime
from app.firebase_init import db
from app.functions.unit import knots_to_kmh, hpa_to_bar
from app.functions.classification import get_localized_tropical_cyclone_classifications

load_dotenv()

# Cache pour éviter les requêtes répétées
data_cache = {
    'last_update': None,
    'data': [],
    'is_updating': False
}

# Configuration d'optimisation
UPDATE_INTERVAL = 1800  # 30 minutes au lieu de 2 heures
CACHE_DURATION = 900    # 15 minutes de cache
REQUEST_TIMEOUT = 300   # Timeout de 5 minutes par source (plus réaliste)

def is_cache_valid():
    """Vérifie si le cache est encore valide."""
    if not data_cache['last_update']:
        return False
    return datetime.now() - data_cache['last_update'] < timedelta(seconds=CACHE_DURATION)

def get_cached_data():
    """Retourne les données du cache si elles sont valides."""
    if is_cache_valid() and data_cache['data']:
        print("📦 Utilisation des données en cache")
        return data_cache['data']
    return None

def update_cache(new_data):
    """Met à jour le cache avec les nouvelles données."""
    data_cache['data'] = new_data
    data_cache['last_update'] = datetime.now()
    print(f"💾 Cache mis à jour avec {len(new_data)} cyclones")

def save_cyclone_data(cyclone):
    try:
        if db:  # Vérifier que Firebase est disponible
            cyclone_ref = db.collection("Cyclones").document(cyclone["idCyclone"])
            cyclone_ref.set(cyclone)
            print(f"Cyclone {cyclone['name']} enregistré avec succès.")
        else:
            print(f"⚠️ Firebase non disponible - Cyclone {cyclone['name']} non enregistré")
    except Exception as e:
        print(f"Erreur lors de l'enregistrement du cyclone {cyclone['name']}: {str(e)}")

def extract_storm_data(storm, storm_id, source):
    """Extrait les données d'un cyclone de manière sécurisée."""
    try:
        name = storm.name if hasattr(storm, 'name') else "Sans nom"
        
        # Gestion sécurisée des tableaux numpy
        if 'vmax' in storm.vars and len(storm.vars['vmax']) > 0:
            vmax_val = storm.vars['vmax'][-1]
            vmax = knots_to_kmh(int(vmax_val)) if not isinstance(vmax_val, np.ndarray) else knots_to_kmh(int(vmax_val[0]))
        else:
            vmax = 0

        if 'mslp' in storm.vars and len(storm.vars['mslp']) > 0:
            mslp_val = storm.vars['mslp'][-1]
            mslp = hpa_to_bar(int(mslp_val)) if not isinstance(mslp_val, np.ndarray) else hpa_to_bar(int(mslp_val[0]))
        else:
            mslp = 0

        if 'lat' in storm.vars and len(storm.vars['lat']) > 0:
            lat_val = storm.vars['lat'][-1]
            lat = float(lat_val) if not isinstance(lat_val, np.ndarray) else float(lat_val[0])
        else:
            lat = 0

        if 'lon' in storm.vars and len(storm.vars['lon']) > 0:
            lon_val = storm.vars['lon'][-1]
            lon = float(lon_val) if not isinstance(lon_val, np.ndarray) else float(lon_val[0])
        else:
            lon = 0

        basin = storm.attrs.get('basin', 'unknown')
        classification = get_localized_tropical_cyclone_classifications(int(vmax), basin)

        return {
            'name': name,
            'idCyclone': storm_id,
            'vmax': vmax,
            'mslp': mslp,
            'lat': lat,
            'lon': lon,
            'classification': classification,
            'basin': basin,
            'is_invest': hasattr(storm, 'invest') and storm.invest,
            'source': source,
            'last_update': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        print(f"Erreur lors de l'extraction des données pour {storm_id}: {str(e)}")
        return None

def get_storms_from_source(source):
    """Récupère les cyclones depuis une source spécifique avec timeout."""
    try:
        print(f"🔄 Tentative de récupération des données depuis {source}...")
        start_time = time.time()
        
        realtime_obj = realtime.Realtime(
            jtwc=True,
            jtwc_source=source,
            ssl_certificate=certifi.where()
        )
        
        # Récupérer la liste des cyclones actifs
        active_storms = realtime_obj.list_active_storms(basin='all')
        storms_data = []

        if active_storms:
            print(f"✅ Cyclones actifs trouvés via {source}: {active_storms}")
            for storm_id in active_storms:
                try:
                    # Vérifier le timeout global (pas par cyclone)
                    elapsed_time = time.time() - start_time
                    if elapsed_time > REQUEST_TIMEOUT:
                        print(f"⏰ Timeout global atteint pour {source} après {elapsed_time:.2f}s")
                        print(f"📊 {len(storms_data)} cyclones récupérés avant timeout")
                        break
                        
                    print(f"🔄 Traitement du cyclone {storm_id}...")
                    storm = realtime_obj.get_storm(storm_id)
                    storm_data = extract_storm_data(storm, storm_id, source)
                    if storm_data:
                        storms_data.append(storm_data)
                        print(f"✅ Cyclone {storm_id} traité avec succès")
                except Exception as e:
                    print(f"❌ Erreur lors du traitement du cyclone {storm_id} depuis {source}: {str(e)}")
                    continue

        elapsed_time = time.time() - start_time
        print(f"⏱️ {source} terminé en {elapsed_time:.2f}s - {len(storms_data)} cyclones")
        return storms_data
    except Exception as e:
        print(f"❌ Source {source} inactive ou inaccessible: {str(e)}")
        return []

def update_cyclones_data_async():
    """Fonction asynchrone pour mettre à jour les données sans bloquer."""
    if data_cache['is_updating']:
        print("🔄 Mise à jour déjà en cours, ignorée")
        return
    
    data_cache['is_updating'] = True
    try:
        all_storms = []
        sources = ['jtwc', 'ucar', 'noaa']
        active_sources = 0
        
        print("🚀 Début de la mise à jour des données cyclones...")
        start_time = time.time()
        
        for source in sources:
            storms = get_storms_from_source(source)
            if storms:
                all_storms.extend(storms)
                active_sources += 1
            time.sleep(1)  # Pause réduite entre chaque source

        if all_storms:
            print(f"📊 Données récupérées depuis {active_sources} source(s) active(s)")
            
            # Supprimer les anciennes données seulement si Firebase est disponible
            if db:
                try:
                    cyclones_ref = db.collection("Cyclones")
                    docs = cyclones_ref.stream()
                    for doc in docs:
                        doc.reference.delete()
                except Exception as e:
                    print(f"⚠️ Erreur lors de la suppression des anciennes données: {e}")

                # Enregistrer les nouvelles données
                for storm in all_storms:
                    save_cyclone_data(storm)
            
            # Mettre à jour le cache
            update_cache(all_storms)
            
            elapsed_time = time.time() - start_time
            print(f"✅ Mise à jour terminée en {elapsed_time:.2f}s - {len(all_storms)} cyclones actifs trouvés.")
        else:
            print("⚠️ Aucun cyclone actif trouvé dans les sources disponibles.")
            
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour: {e}")
    finally:
        data_cache['is_updating'] = False

def force_update_cyclones_data():
    """Force une mise à jour immédiate des données (pour l'API)."""
    print("🔄 Mise à jour forcée des données cyclones...")
    update_cyclones_data_async()

def initialize_cache_from_firebase():
    """Initialise le cache avec les données Firebase existantes."""
    try:
        if db:
            print("🔄 Initialisation du cache avec les données Firebase existantes...")
            cyclones_ref = db.collection("Cyclones")
            docs = cyclones_ref.stream()
            existing_cyclones = [doc.to_dict() for doc in docs]
            
            if existing_cyclones:
                update_cache(existing_cyclones)
                print(f"✅ Cache initialisé avec {len(existing_cyclones)} cyclones existants")
            else:
                print("⚠️ Aucune donnée existante dans Firebase")
        else:
            print("⚠️ Firebase non disponible pour l'initialisation du cache")
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation du cache: {e}")

def update_cyclones_data():
    """Fonction principale qui gère la mise à jour périodique."""
    # Initialiser le cache avec les données existantes
    initialize_cache_from_firebase()
    
    # Première mise à jour immédiate
    update_cyclones_data_async()
    
    while True:
        time.sleep(UPDATE_INTERVAL)  # Attendre 30 minutes
        update_cyclones_data_async()
