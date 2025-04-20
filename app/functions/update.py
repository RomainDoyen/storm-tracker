import os
import time
import ssl
import certifi
import numpy as np
from dotenv import load_dotenv
from tropycal import realtime
from app.firebase_init import db
from app.functions.unit import knots_to_kmh, hpa_to_bar
from app.functions.classification import get_localized_tropical_cyclone_classifications

load_dotenv()

def save_cyclone_data(cyclone):
    try:
        cyclone_ref = db.collection("Cyclones").document(cyclone["idCyclone"])
        cyclone_ref.set(cyclone)
        print(f"Cyclone {cyclone['name']} enregistré avec succès.")
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
    """Récupère les cyclones depuis une source spécifique."""
    try:
        print(f"Tentative de récupération des données depuis {source}...")
        realtime_obj = realtime.Realtime(
            jtwc=True,
            jtwc_source=source,
            ssl_certificate=certifi.where()
        )
        active_storms = realtime_obj.list_active_storms(basin='all')
        storms_data = []

        if active_storms:
            print(f"Cyclones actifs trouvés via {source}: {active_storms}")
            for storm_id in active_storms:
                try:
                    storm = realtime_obj.get_storm(storm_id)
                    storm_data = extract_storm_data(storm, storm_id, source)
                    if storm_data:
                        storms_data.append(storm_data)
                except Exception as e:
                    print(f"Erreur lors du traitement du cyclone {storm_id} depuis {source}: {str(e)}")
                    continue

        return storms_data
    except Exception as e:
        print(f"Source {source} inactive ou inaccessible: {str(e)}")
        return []

def update_cyclones_data():
    while True:
        all_storms = []
        sources = ['jtwc', 'ucar', 'noaa']
        active_sources = 0
        
        for source in sources:
            storms = get_storms_from_source(source)
            if storms:
                all_storms.extend(storms)
                active_sources += 1
            time.sleep(2)  # Petite pause entre chaque source

        if all_storms:
            print(f"Données récupérées depuis {active_sources} source(s) active(s)")
            # Supprimer les anciennes données
            cyclones_ref = db.collection("Cyclones")
            docs = cyclones_ref.stream()
            for doc in docs:
                doc.reference.delete()

            # Enregistrer les nouvelles données
            for storm in all_storms:
                save_cyclone_data(storm)
            
            print(f"Mise à jour terminée. {len(all_storms)} cyclones actifs trouvés.")
        else:
            print("Aucun cyclone actif trouvé dans les sources disponibles.")

        time.sleep(960)  # Pause de 2 heures avant de mettre à jour les données
