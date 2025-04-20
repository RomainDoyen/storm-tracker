from flask import render_template, jsonify
from app import app
import datetime
import os
from app.firebase_init import db
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
        cyclones_ref = db.collection("Cyclones")
        cyclones = [doc.to_dict() for doc in cyclones_ref.stream()]
        return jsonify(cyclones)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
