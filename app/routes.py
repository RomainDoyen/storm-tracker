import datetime

from flask import jsonify, render_template

from app import app
from app.db import database_available, list_cyclones
from app.functions.update import get_cached_data, run_live_update, update_in_progress


@app.route('/')
@app.route('/index')
def index():
    title_site = {'title': 'Traqueur de Tempêtes'}
    year = datetime.date.today().year
    return render_template(
        'index.html',
        title='Accueil',
        title_site=title_site,
        year=year,
    )


@app.route('/cyclones-data')
def cyclones_data():
    try:
        cached_data = get_cached_data()
        if cached_data is not None:
            return jsonify(cached_data)

        if database_available():
            return jsonify(list_cyclones())
        return jsonify([])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/force-update', methods=['POST'])
def force_update():
    """Récupère les bulletins et ne répond qu'une fois le stock remplacé."""
    try:
        storms = run_live_update()
        if storms is None:
            return jsonify({
                "status": "error",
                "message": "La récupération des bulletins a échoué",
            }), 500
        return jsonify({
            "status": "success",
            "cyclones": storms,
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
        }), 500


@app.route('/status')
def status():
    """Retourne le statut de l'application."""
    try:
        cached_data = get_cached_data()
        return jsonify({
            "status": "online",
            "is_updating": update_in_progress(),
            "cache_available": cached_data is not None,
            "cyclones_count": len(cached_data) if cached_data is not None else 0,
            "database_available": database_available(),
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
        }), 500
