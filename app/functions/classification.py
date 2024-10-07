def get_localized_tropical_cyclone_classifications(max_wind, basin):
    basin_mapping = {
        'north_atlantic': 'al',
        'east_pacific': 'EP',
        'west_pacific': 'WP',
        'south_indian': 'SH',
        'north_indian': 'IO',
    }

    basin_abbreviation = basin_mapping.get(basin.lower(), None)

    if max_wind <= 0 or basin_abbreviation is None:
        return 'NO DATA'

    if basin_abbreviation in ['al', 'cp', 'EP', 'NA', 'SA', 'SL', 'CS', 'GM']:
        return get_nhc_classifications(max_wind)
    elif basin_abbreviation == 'WP':
        return get_jtwc_classifications(max_wind)
    elif basin_abbreviation in ['SH', 'SP', 'WA', 'EA']:
        return get_australia_classifications(max_wind)
    elif basin_abbreviation in ['IO', 'NI', 'AS', 'BB']:
        return get_n_indian_classifications(max_wind)
    elif basin_abbreviation == 'SI':
        return get_sw_indian_classifications(max_wind)
    else:
        return 'NO DATA'

def get_nhc_classifications(max_wind=0):
    if max_wind <= 33:
        return 'Dépression tropicale'
    elif 34 <= max_wind <= 63:
        return 'Tempête tropicale'
    elif 64 <= max_wind <= 82:
        return 'Ouragan de catégorie 1'
    elif 83 <= max_wind <= 95:
        return 'Ouragan de catégorie 2'
    elif 96 <= max_wind <= 112:
        return 'Ouragan de catégorie 3'
    elif 113 <= max_wind <= 136:
        return 'Ouragan de catégorie 4'
    elif max_wind > 136:
        return 'Ouragan de catégorie 5'
    else:
        return 'NO DATA'

def get_jtwc_classifications(max_wind=0):
    if max_wind <= 33:
        return 'Dépression tropicale'
    elif 34 <= max_wind <= 63:
        return 'Tempête tropicale'
    elif 64 <= max_wind <= 129:
        return 'Typhon'
    elif max_wind > 129:
        return 'Super Typhon'
    else:
        return 'NO DATA'

def get_australia_classifications(max_wind=0):
    if max_wind < 34:
        return 'Perturbation tropicale/dépression/dépression'
    elif 34 <= max_wind <= 47:
        return 'Cyclone tropical de catégorie 1'
    elif 48 <= max_wind <= 63:
        return 'Cyclone tropical de catégorie 2'
    elif 64 <= max_wind <= 85:
        return 'Cyclone tropical de catégorie 3'
    elif 86 <= max_wind <= 107:
        return 'Cyclone tropical de catégorie 4'
    elif max_wind >= 108:
        return 'Cyclone tropical de catégorie 5'
    else:
        return 'NO DATA'

def get_n_indian_classifications(max_wind=0):
    if max_wind < 17:
        return 'Zone de basse pression'
    elif 17 <= max_wind <= 27:
        return 'Dépression'
    elif 28 <= max_wind <= 33:
        return 'Dépression profonde'
    elif 34 <= max_wind <= 47:
        return 'Tempête cyclonique'
    elif 48 <= max_wind <= 63:
        return 'Tempête cyclonique violente'
    elif 64 <= max_wind <= 89:
        return 'Tempête cyclonique très violente'
    elif 90 <= max_wind <= 120:
        return 'Tempête cyclonique extrêmement violente'
    elif max_wind > 120:
        return 'Tempête super cyclonique'
    else:
        return 'NO DATA'


def get_sw_indian_classifications(max_wind=0):
    if max_wind < 28:
        return 'Zone de temps perturbé'
    elif 28 <= max_wind <= 29:
        return 'Perturbation tropicale'
    elif 30 <= max_wind <= 33:
        return 'Dépression tropicale'
    elif 34 <= max_wind <= 47:
        return 'Tempête tropicale modérée'
    elif 48 <= max_wind <= 63:
        return 'Tempête tropicale sévère'
    elif 64 <= max_wind <= 85:
        return 'Cyclone tropical'
    elif 86 <= max_wind <= 113:
        return 'Cyclone tropical intense'
    elif max_wind > 113:
        return 'Cyclone tropical très intense'
    else:
        return 'NO DATA'