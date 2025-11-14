# app.py

import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import re
from typing import List, Dict

import spacy # <-- NOUVEAU : Import de spaCy

# Importer les moteurs que nous avons construits
from yelp_api import search_businesses, get_reviews_for_business
from nlp_engine import calculate_cas, CRITERIA # CRITERIA est importé pour la classification des scénarios

# --- 0. INITIALISATION SPACY (Modèle NLP) ---
# Charger le modèle une seule fois au démarrage de l'application
try:
    # Utilisez spacy.load() comme indiqué par votre console
    NLP_MODEL = spacy.load("en_core_web_sm")
    print("✔ Modèle spaCy 'en_core_web_sm' chargé avec succès.")
except Exception as e:
    print(f"FATAL ERROR: Impossible de charger le modèle spaCy: {e}")
    NLP_MODEL = None # Le programme peut continuer mais sans fonctionnalité NLP

# --- 1. Initialisation de la Sécurité et des Variables ---
load_dotenv()
YELP_API_KEY = os.getenv("YELP_API_KEY")

if not YELP_API_KEY:
    print("FATAL ERROR: YELP_API_KEY non trouvé. Le programme va planter.")

DEFAULT_LOCATION = os.getenv("DEFAULT_LOCATION", "Paris, FR")
DEFAULT_CATEGORIES = os.getenv("DEFAULT_CATEGORIES", "plumbers") # Nous simplifions ici pour la démo

app = Flask(__name__)
CORS(app) # <--- 2. Ajout pour le CORS
# --- 2. Fonctions Utilitaires : Classification du Scénario ---
# ... (pas de changement dans classify_scenario) ...
def classify_scenario(user_text: str) -> str:
    """
    Classifie la demande utilisateur dans l'un des scénarios de démonstration.
    Ceci est une simulation basée sur des mots-clés simples pour le Hackathon.
    """
    text = user_text.lower()
    
    # Critères pour le Scénario 1 : Urgence / Crise
    # Les mots-clés "urgent" et "crise" sont des indicateurs forts
    if any(word in text for word in ["urgent", "panicking", "crisis", "emergency", "immediately", "pipe"]):
        return "urgence"
    
    # Critères pour le Scénario 2 : Planification / Qualité
    # Les mots-clés "patient", "expliqué" et "rénovation" sont des indicateurs
    if any(word in text for word in ["patient", "communicative", "old system", "historic", "renovation", "detailed"]):
        return "planification"
        
    # Par défaut, si aucune classification claire, choisir le scénario 1 pour la démo
    return "urgence"

# --- 3. Définition de la Route API Principale ---

@app.route('/match', methods=['POST'])
def match_artisan():
    """
    Route principale qui reçoit la demande de l'utilisateur et renvoie les artisans triés par CAS.
    """
    try:
        # ... (le début de la fonction reste le même) ...
        data = request.json
        user_description = data.get("description")
        location = data.get("location", DEFAULT_LOCATION)
        search_category = data.get("category", DEFAULT_CATEGORIES)
        
        if not user_description:
            return jsonify({"error": "La description utilisateur est requise."}), 400

        # Vérification du modèle NLP (Sécurité pour le déploiement)
        if not NLP_MODEL:
            return jsonify({
                "status": "error",
                "message": "Le moteur NLP n'est pas chargé. Impossible de calculer le CAS Score."
            }), 500
        
        # A. Classification du Scénario
        scenario_key = classify_scenario(user_description)
        criteria_term = CRITERIA.get(scenario_key, {}).get("term", "Adéquation Contextuelle")

        print(f"Demande utilisateur: '{user_description}'")
        print(f"Scénario classifié: {scenario_key} ({criteria_term})")
        
        # B. Recherche d'Artisans (Moteur Yelp API)
        businesses = search_businesses(
            term=search_category,
            location=location,
            limit=10 
        )
        
        if not businesses:
            return jsonify({
                "status": "success",
                "message": f"Aucun artisan trouvé pour '{search_category}' à {location}. Vérifiez l'API Yelp.",
                "results": []
            }), 200

        # C. Analyse et Calcul du CAS (Moteur NLP)
        scored_artisans: List[Dict] = []
        
        for biz in businesses:
            business_id = biz["id"]
            
            # 1. Récupérer les Revues de Yelp
            reviews = get_reviews_for_business(business_id)
            
            # 2. Calculer le Score d'Adéquation Contextuelle (CAS)
            avg_rating = biz.get("rating", 3.0) 
            
            # ATTENTION : Passage du modèle chargé en argument !
            cas_score, proofs = calculate_cas(
                reviews, 
                scenario_key, 
                avg_rating,
                nlp_model=NLP_MODEL # <-- MODIFICATION : Passage du modèle
            )
            
            # ... (le reste de la boucle reste le même) ...
            artisan_result = {
                "name": biz["name"],
                "yelp_rating": avg_rating,
                "review_count": biz["review_count"],
                "cas_score": cas_score,
                "proofs": proofs,  # Les citations de revues pour la démo
                "url": biz.get("url"),
                "scenario_term": criteria_term
            }
            scored_artisans.append(artisan_result)

        # D. Triage des Résultats
        final_results = sorted(scored_artisans, key=lambda x: x["cas_score"], reverse=True)

        return jsonify({
            "status": "success",
            "message": f"{len(final_results)} artisans triés par {criteria_term}.",
            "scenario": scenario_key,
            "results": final_results
        }), 200

    except Exception as e:
        print(f"Erreur interne du serveur: {e}")
        return jsonify({"error": f"Erreur interne: {str(e)}"}), 500


# --- 4. Route de Test (Home) ---
@app.route('/')
def home():
    return jsonify({
        "status": "ArtisanTrust Backend is running!",
        "message": "Utilisez la route /match avec une méthode POST pour tester l'application."
    })

# --- 5. Point de Lancement ---
if __name__ == '__main__':
    # La ligne app.run(debug=True) est ignorée par Gunicorn en production.
    app.run(debug=True)