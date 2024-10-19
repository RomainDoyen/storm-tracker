from flask import render_template, jsonify
from app import app
import datetime
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.getenv("SUPABASE_URL") # type: ignore
key: str = os.getenv("SUPABASE_KEY") # type: ignore
supabase: Client = create_client(url, key)

@app.route('/')
@app.route('/index')
def index():
    title_site = {'title': 'Traqueur de Tempêtes'}
    year = datetime.date.today().year
    return render_template('index.html', title='Accueil', title_site=title_site, year=year)

@app.route('/cyclones-data')
def cyclones_data():
    try:
        response = supabase.table("Cyclones").select("*").execute()
        cyclones = response.data
        return jsonify(cyclones)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
