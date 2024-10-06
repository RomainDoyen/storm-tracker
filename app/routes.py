import json
import os
from flask import jsonify, render_template
from app import app
import datetime
from app.functions.update import update_cyclones_data

@app.route('/')
@app.route('/index')
def index():
    title_site = {'title': 'Traqueur de Tempêtes'}
    year = datetime.date.today().year
    return render_template('index.html', title='Accueil', title_site=title_site, year=year)

@app.route('/cyclones-data')
def cyclones_data():
    json_file_path = os.path.join(app.root_path, 'static', 'data', 'cyclones.json')

    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as json_file:
            cyclones = json.load(json_file)
    else:
        update_cyclones_data()
        with open(json_file_path, 'r') as json_file:
            cyclones = json.load(json_file)

    return jsonify(cyclones)