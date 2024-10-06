from flask import render_template
from app import app
import datetime

@app.route('/')
@app.route('/index')
def index():
    title_site = {'title': 'Traqueur de Tempêtes'}
    year = datetime.date.today().year
    return render_template('index.html', title='Accueil', title_site=title_site, year=year)
