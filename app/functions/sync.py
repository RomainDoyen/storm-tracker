from datetime import timedelta


def sync_cyclone_store(store, storms, fetch_succeeded):
    """Remplace les cyclones stockés après une récupération réussie.

    Une récupération vide signifie qu'aucun cyclone n'est actif : les fiches
    précédentes sont retirées. Un échec laisse le stock inchangé.
    """
    if not fetch_succeeded:
        return False

    for storm in storms:
        store.save(storm)

    current_ids = {storm['idCyclone'] for storm in storms}
    for existing_id in list(store.list_ids()):
        if existing_id not in current_ids:
            store.delete(existing_id)
    return True


def cached_payload(data, last_update, now, duration_seconds):
    """Retourne le cache encore valable, y compris une liste vide."""
    if last_update is None or data is None:
        return None
    if now - last_update < timedelta(seconds=duration_seconds):
        return data
    return None
