import os

from flask import Flask

app = Flask(__name__)

from app import routes

if os.getenv('STORM_TRACKER_DISABLE_UPDATER') != '1':
    from app.functions.update import start_background_updates
    start_background_updates()
