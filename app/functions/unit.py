def knots_to_kmh(knots):
    return knots * 1.852

def hpa_to_bar(hpa):
    return hpa / 1000.0

def present_observation(vmax_knots, mslp_hpa, basin):
    """Affiche le vent en km/h et la pression en bar, et classe à partir des nœuds."""
    from app.functions.classification import get_localized_tropical_cyclone_classifications

    return {
        'vmax': float(round(knots_to_kmh(vmax_knots), 2)),
        'mslp': float(round(hpa_to_bar(mslp_hpa), 3)),
        'classification': get_localized_tropical_cyclone_classifications(int(vmax_knots), basin),
    }