import os
import time
from dotenv import load_dotenv
from tropycal import realtime
from supabase import create_client, Client
from app.functions.unit import knots_to_kmh, hpa_to_bar
from app.functions.classification import get_localized_tropical_cyclone_classifications

load_dotenv()

url: str = os.getenv("SUPABASE_URL") # type: ignore
key: str = os.getenv("SUPABASE_KEY") # type: ignore
supabase: Client = create_client(url, key)

def save_cyclone_data(cyclone):
    try:
        response = supabase.table("Cyclones").select("idCyclone").eq("idCyclone", cyclone["idCyclone"]).execute()

        if response.data:
            update_response = (
                supabase
                .table("Cyclones")
                .update(cyclone)
                .eq("idCyclone", cyclone["idCyclone"])
                .execute()
            )
            print(f"Cyclone {cyclone['name']} mis à jour avec succès.")
        else:
            insert_response = (
                supabase
                .table("Cyclones")
                .insert(cyclone)
                .execute()
            )
            print(f"Cyclone {cyclone['name']} créé avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'enregistrement du cyclone {cyclone['name']}: {str(e)}")

def update_cyclones_data():
    while True:
        realtime_obj = realtime.Realtime(jtwc=True, jtwc_source="jtwc")
        active_storms_indian_ocean = realtime_obj.list_active_storms(basin='all')

        if active_storms_indian_ocean:
            for storm_id in active_storms_indian_ocean:
                storm = realtime_obj.get_storm(storm_id)

                name = storm.name
                vmax = knots_to_kmh(int(storm.vars['vmax'][-1]))
                mslp = hpa_to_bar(int(storm.vars['mslp'][-1]))
                lat = float(storm.vars['lat'][-1])
                lon = float(storm.vars['lon'][-1])
                basin = storm.attrs['basin']

                classification = get_localized_tropical_cyclone_classifications(int(vmax), basin)

                cyclone_data = {
                    'name': name,
                    'idCyclone': storm_id,
                    'vmax': vmax,
                    'mslp': mslp,
                    'lat': lat,
                    'lon': lon,
                    'classification': classification,
                }

                save_cyclone_data(cyclone_data)

        time.sleep(600)  # Pause de 10 minutes avant de mettre à jour les données
