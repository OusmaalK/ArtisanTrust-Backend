# yelp_api.py

import os
import requests
from dotenv import load_dotenv

# Charger les variables d'environnement (pour YELP_API_KEY)
load_dotenv()
API_KEY = os.getenv("YELP_API_KEY")

# URL de base pour l'API Yelp Fusion
YELP_BASE_URL = "https://api.yelp.com/v3/"

# L'en-tête d'authentification requis pour toutes les requêtes
HEADERS = {
    "Authorization": f"Bearer {API_KEY}"
}


def search_businesses(term: str, location: str, limit: int = 10) -> list:
    """
    Recherche des établissements (artisans) sur Yelp.

    Args:
        term (str): Le terme de recherche (ex: 'plumbers', 'electricians').
        location (str): La ville ou l'adresse pour la recherche.
        limit (int): Le nombre maximum de résultats à retourner.

    Returns:
        list: Une liste de dictionnaires contenant les données de base des artisans.
    """
    url = f"{YELP_BASE_URL}businesses/search"
    params = {
        "term": term,
        "location": location,
        "limit": limit,
        "categories": os.getenv("DEFAULT_CATEGORIES", "homeandgarden")
    }

    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()  # Lance une exception si la réponse est une erreur HTTP
        data = response.json()
        return data.get("businesses", [])
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la recherche Yelp : {e}")
        return []


def get_reviews_for_business(business_id: str) -> list:
    """
    Récupère jusqu'à trois critiques pour un établissement donné.

    ATTENTION : L'API Yelp Fusion limite souvent le nombre de revues à 3 pour des raisons de performance.
    Pour un Hackathon, cela sera suffisant pour la démo, mais il faut le noter.

    Args:
        business_id (str): L'ID unique de l'établissement Yelp.

    Returns:
        list: Une liste de dictionnaires contenant le texte des critiques.
    """
    url = f"{YELP_BASE_URL}businesses/{business_id}/reviews"

    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        # Nous retournons le texte et le rating de chaque revue
        reviews = [
            {"text": r["text"], "rating": r["rating"]}
            for r in data.get("reviews", [])
        ]
        return reviews
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération des revues pour {business_id} : {e}")
        return []

# --- Fonction de Test (Optionnelle, pour vérifier la connexion) ---
if __name__ == '__main__':
    # Ceci s'exécute uniquement si vous lancez ce fichier directement
    test_location = os.getenv("DEFAULT_LOCATION", "Paris, FR")
    
    print(f"--- Test de Recherche d'Artisans à {test_location} ---")
    
    # 1. Rechercher les plombiers
    plumbers = search_businesses("plumbers", test_location, limit=3)
    
    if plumbers:
        print(f"Trouvé {len(plumbers)} plombiers. Exemple: {plumbers[0]['name']}")
        
        # 2. Récupérer les revues pour le premier plombier trouvé
        first_plumber_id = plumbers[0]["id"]
        print(f"\n--- Test de Récupération des Revues pour {plumbers[0]['name']} ---")
        
        reviews = get_reviews_for_business(first_plumber_id)
        
        if reviews:
            print(f"Revues trouvées ({len(reviews)}):")
            print(reviews[0]["text"][:100] + "...")
        else:
            print("Aucune revue trouvée.")
    else:
        print("Aucun établissement trouvé. Vérifiez la clé API et la localisation.")