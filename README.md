# Storm Tracker 🌀

Une application web qui suit en temps réel les tempêtes et cyclones à travers le monde. Elle utilise l'API [Tropycal](https://tropycal.github.io/tropycal/index.html) pour récupérer les données et Firebase pour le stockage.

## Fonctionnalités

- 🗺️ Carte interactive des tempêtes actives
- 🔄 Mise à jour en temps réel des données
- 📱 Interface responsive
- 🌍 Couverture mondiale des cyclones
- 📊 Détails sur chaque tempête (vitesse des vents, pression, classification)

## Prérequis

- Python 3.8 ou supérieur
- Un compte Firebase
- pip (gestionnaire de paquets Python)

## Installation

1. Clonez le dépôt

```bash
git clone https://github.com/RomainDoyen/storm-tracker.git
cd storm-tracker
```

2. Installez les dépendances

```bash
pip install -r requirements.txt
```

3. Configuration de Firebase

- Créez un projet sur [Firebase Console](https://console.firebase.google.com/)
- Activez Firestore Database dans votre projet
- Générez un fichier de configuration d'administration (clé privée) :
  - Allez dans Paramètres du projet > Comptes de service
  - Cliquez sur "Générer une nouvelle clé privée"
  - Sauvegardez les informations pour les variables d'environnement

4. Configurez les variables d'environnement

Créez un fichier `.env` à la racine du projet avec les informations suivantes :

```env
# Firebase Configuration (Admin SDK)
FIREBASE_TYPE=service_account
FIREBASE_PROJECT_ID=votre-projet-id
FIREBASE_PRIVATE_KEY_ID=votre-private-key-id
FIREBASE_PRIVATE_KEY="votre-private-key"
FIREBASE_CLIENT_EMAIL=votre-client-email
FIREBASE_CLIENT_ID=votre-client-id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_X509_CERT_URL=votre-cert-url
FIREBASE_UNIVERSE_DOMAIN=googleapis.com

# Firebase Web Config
FIREBASE_API_KEY=votre-api-key
FIREBASE_AUTH_DOMAIN=votre-projet.firebaseapp.com
FIREBASE_PROJECT_ID_WEB=votre-projet-id
FIREBASE_STORAGE_BUCKET=votre-projet.appspot.com
FIREBASE_MESSAGING_SENDER_ID=votre-sender-id
FIREBASE_APP_ID=votre-app-id
```

5. Lancez l'application

```bash
python run.py
```

L'application sera accessible à l'adresse [http://127.0.0.1:7000/](http://127.0.0.1:7000/)

## Structure des données Firebase

La collection `Cyclones` dans Firestore stocke les informations suivantes pour chaque tempête :

```javascript
{
  "idCyclone": "string",    // Identifiant unique du cyclone
  "name": "string",         // Nom du cyclone
  "vmax": number,          // Vitesse maximale des vents (km/h)
  "mslp": number,          // Pression au niveau de la mer (bar)
  "lat": number,           // Latitude
  "lon": number,           // Longitude
  "classification": "string", // Classification du cyclone
  "basin": "string",       // Bassin océanique
  "is_invest": boolean,    // Si c'est une zone d'investigation
  "source": "string",      // Source des données (JTWC, NOAA, etc.)
  "last_update": "string"  // Date de dernière mise à jour
}
```

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

