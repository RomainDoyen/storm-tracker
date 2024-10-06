from app import app
import os
import json
import time
from tropycal import realtime
from app.functions.unit import knots_to_kmh, hpa_to_bar
from app.functions.classification import get_localized_tropical_cyclone_classifications

def update_cyclones_data():
    while True:
        json_file_path = os.path.join(app.root_path, 'static', 'data', 'cyclones.json')
        
        realtime_obj = realtime.Realtime(jtwc=True, jtwc_source="jtwc")
        active_storms_indian_ocean = realtime_obj.list_active_storms(basin='all')

        cyclones = []

        if active_storms_indian_ocean:
            for storm_id in active_storms_indian_ocean:
                storm = realtime_obj.get_storm(storm_id)
                # storm_data = storm.get_realtime_info()

                name = storm.name
                vmax = knots_to_kmh(int(storm.vars['vmax'][-1]))
                mslp = hpa_to_bar(int(storm.vars['mslp'][-1]))
                lat = float(storm.vars['lat'][-1])
                lon = float(storm.vars['lon'][-1])
                basin = storm.attrs['basin']
                
                # print(f"ID: {storm_id}, Basin: {basin}, Vmax: {vmax}")
                
                classification = get_localized_tropical_cyclone_classifications(int(vmax), basin)

                cyclones.append({
                    'name': name,
                    'id': storm_id,
                    'vmax': vmax,
                    'mslp': mslp,
                    'lat': lat,
                    'lon': lon,
                    'classification': classification,
                })

        with open(json_file_path, 'w') as json_file:
            json.dump(cyclones, json_file)

        time.sleep(600)