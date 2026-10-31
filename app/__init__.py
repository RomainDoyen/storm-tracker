import os

from flask import Flask

app = Flask(__name__)

from app import routes


def _restart_after_fork():
    from app.db import reset_after_fork as reset_db
    from app.functions.update import reset_after_fork as reset_updater
    from app.functions.update import start_background_updates
    reset_db()
    reset_updater()
    if os.getenv('STORM_TRACKER_DISABLE_UPDATER') != '1':
        start_background_updates()


if hasattr(os, "register_at_fork"):
    os.register_at_fork(after_in_child=_restart_after_fork)

if os.getenv('STORM_TRACKER_DISABLE_UPDATER') != '1':
    from app.functions.update import start_background_updates
    start_background_updates()
