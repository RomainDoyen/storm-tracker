import os

# Un seul worker : le fil de mise à jour et Neon n'ont pas à être dupliqués.
# Pas de preload : le worker importe l'application après le fork.
workers = 1
timeout = 120
preload_app = False
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"
