from flask import render_template, jsonify, request
from app import app
import datetime
import os
import threading
from app.firebase_init import db
from app.functions.update import force_update_cyclones_data, get_cached_data
from dotenv import load_dotenv

load_dotenv()

@app.route('/')
@app.route('/index')
def index():
    title_site = {'title': 'Traqueur de Tempêtes'}
    year = datetime.date.today().year
    
    # Configuration Firebase pour le template
    firebase_config = {
        'api_key': os.getenv('FIREBASE_API_KEY'),
        'auth_domain': os.getenv('FIREBASE_AUTH_DOMAIN'),
        'project_id': os.getenv('FIREBASE_PROJECT_ID_WEB'),
        'storage_bucket': os.getenv('FIREBASE_STORAGE_BUCKET'),
        'messaging_sender_id': os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
        'app_id': os.getenv('FIREBASE_APP_ID')
    }
    
    return render_template('index.html', 
                          title='Accueil', 
                          title_site=title_site, 
                          year=year,
                          firebase_config=firebase_config)

@app.route('/cyclones-data')
def cyclones_data():
    try:
        # Essayer d'abord le cache
        cached_data = get_cached_data()
        if cached_data:
            return jsonify(cached_data)
        
        # Sinon, récupérer depuis Firebase
        if db:
            cyclones_ref = db.collection("Cyclones")
            cyclones = [doc.to_dict() for doc in cyclones_ref.stream()]
            return jsonify(cyclones)
        else:
            return jsonify({"error": "Firebase non disponible"}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/force-update', methods=['POST'])
def force_update():
    """Force une mise à jour des données cyclones."""
    try:
        # Lancer la mise à jour en arrière-plan
        thread = threading.Thread(target=force_update_cyclones_data)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "status": "success",
            "message": "Mise à jour lancée en arrière-plan"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/status')
def status():
    """Retourne le statut de l'application."""
    try:
        cached_data = get_cached_data()
        return jsonify({
            "status": "online",
            "cache_available": cached_data is not None,
            "cyclones_count": len(cached_data) if cached_data else 0,
            "firebase_available": db is not None
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
