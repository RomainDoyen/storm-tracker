import os
import firebase_admin
from firebase_admin import credentials, firestore

# Chemin vers le fichier de clé de service Firebase
firebase_key_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                'storm-tracker-c164a-firebase-adminsdk-fbsvc-86bd6d4c10.json')

# Vérifier si le fichier de clé existe
if os.path.exists(firebase_key_path):
    # Initialisation de Firebase avec le fichier de clé de service
    cred = credentials.Certificate(firebase_key_path)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Firebase initialisé avec succès")
else:
    # Mode développement sans Firebase
    db = None
    print("⚠️  Mode développement : Fichier de clé Firebase non trouvé") 