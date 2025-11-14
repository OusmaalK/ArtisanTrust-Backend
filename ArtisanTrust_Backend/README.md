# 🛠️ ArtisanTrust : Le Moteur d'Appariement Contextuel (CAS Score)

## 🚀 Concept du Projet

**ArtisanTrust** est une solution backend innovante qui résout le problème de la sélection d'artisans en cas de crise. Nous introduisons le **Score d'Adéquation Contextuelle (CAS Score)**, une métrique basée sur l'Intelligence Artificielle qui évalue l'artisan non pas sur sa note générale (comme Yelp), mais sur son **aptitude psychologique et technique** à répondre à une demande spécifique et urgente.

L'objectif est de dépasser le simple 5/5 pour trouver l'artisan le **mieux adapté**.

## 🧠 L'Innovation : Le CAS Score

Le CAS Score combine deux éléments pour le score final :

1.  **Score de Base (40%):** Basé sur la Note Yelp de l'artisan (preuve de compétence générale).
2.  **Bonus IA (60%):** Calculé via le Traitement du Langage Naturel (NLP) qui analyse les revues pour trouver des mots-clés liés au contexte de l'utilisateur (ex: "calme," "réactif," "crise").

*(Pour la démonstration, une **Heuristique de Robustesse** a été implémentée pour garantir l'affichage du Bonus IA même en cas d'échec de l'API Yelp à fournir des revues.)*

## 🏗️ Structure du Projet

-   `app.py`: Point d'entrée de l'API Flask et gestion du routage (`/match`).
-   `nlp_engine.py`: Contient la logique du CAS Score, la classification des scénarios d'urgence, et l'algorithme d'analyse des revues.
-   `.env`: Fichier de configuration pour la clé d'API Yelp et la localisation par défaut.
-   `requirements.txt`: Liste des dépendances.

## ⚙️ Installation et Démarrage

### Prérequis

* Python 3.x
* Clé d'API Yelp Fusion (pour le fichier `.env`)

### Étapes d'Installation

1.  **Cloner le dépôt :**
    ```bash
    git clone [VOTRE_LIEN_GIT] ArtisanTrust_Backend
    cd ArtisanTrust_Backend
    ```

2.  **Créer et Activer l'Environnement Virtuel :**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Installer les Dépendances :**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration des Variables :**
    Créez un fichier `.env` à la racine du projet et ajoutez votre clé Yelp :
    ```env
    YELP_API_KEY="VOTRE_CLÉ_YELP_ICI"
    DEFAULT_LOCATION="New York, NY"
    ```

5.  **Lancer le Serveur :**
    ```bash
    python app.py
    ```
    Le serveur démarrera sur `http://127.0.0.1:5000`.

## 🚀 Démonstration (Test de l'Endpoint /match)

Utilisez cette commande dans votre console PowerShell pour tester l'algorithme d'urgence et voir le classement basé sur le **CAS Score**.

### Commande de Test (Urgence : Calme et Rapide)

```powershell
Invoke-RestMethod -Uri "[http://127.0.0.1:5000/match](http://127.0.0.1:5000/match)" -Method Post -ContentType "application/json" -Body '{"description": "URGENT burst pipe! I''m panicking, I need someone who is super CALM and fast.", "category": "plumbers"}' | Select-Object -ExpandProperty results | Select-Object @{Name="CAS Score";Expression={$_.cas_score}}, @{Name="Note Yelp";Expression={$_.yelp_rating}}, @{Name="Nom de l'Artisan";Expression={$_.name}}, @{Name="Preuves IA";Expression={$_.proofs}} | Format-Table -AutoSize