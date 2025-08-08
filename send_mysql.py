"""
Description : Ce script lit un fichier CSV contenant des données de métriques, effectue un traitement 
préliminaire pour nettoyer et convertir les données, puis insère les résultats dans une base de données MySQL. 

Fonctionnalités principales :
- Chargement d'un fichier CSV.
- Remplacement des valeurs infinies par NaN pour éviter des erreurs lors du traitement.
- Conversion des colonnes spécifiques en types numériques pour garantir la cohérence des données.
- Insertion des données traitées dans une table MySQL.

Prérequis :
- Une base de données MySQL configurée avec une table `ue_metrics`.
- Les bibliothèques Python nécessaires : `pandas`, `numpy`, et `sqlalchemy`.

"""



import pandas as pd
from sqlalchemy import create_engine
import numpy as np

try:
    # Chemin du fichier CSV
    file_path = '/home/rufus/srsran_projet/metrics_timestamp.csv'

    # Charger les données CSV et renommer la colonne 'time' en 'temps'
    data = pd.read_csv(file_path, delimiter=';', on_bad_lines='skip')
    print("Données chargées avec succès.")
    
    # Remplacer les valeurs infinies par NaN
    data.replace([np.inf, -np.inf], np.nan, inplace=True)
    print("Données après remplacement des valeurs inf :")
    print(data.head())  # Afficher les premières lignes pour vérifier

    # Convertir la colonne 'pl' en float
    data['pl'] = pd.to_numeric(data['pl'], errors='coerce')
    print("Données après conversion de la colonne 'pl' :")
    print(data.head())  # Afficher les premières lignes pour vérifier

    # Connexion à la base de données
    engine = create_engine('mysql+pymysql://root:Birame#04@localhost:3306/ue_metrics_db')
    print("Connexion à la base de données réussie.")
    
    # Insérer les données dans la table ue_metrics
    data.to_sql('ue_metrics', con=engine, if_exists='append', index=False)
    print("Données insérées avec succès.")
except Exception as e:
    print(f"Erreur: {e}")

