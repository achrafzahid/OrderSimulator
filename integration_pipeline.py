import pandas as pd
import os
from google.cloud import bigquery
from google.cloud import storage
from datetime import datetime

# --- CONFIGURATION ---
PROJECT_ID = "votre-projet-id"
DATASET_ID = "globalshop_dw"
TABLE_ID = "orders"
BUCKET_NAME = "globalshop-raw"
TABLE_REF = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

def clean_and_normalize(df, file_name):
    """
    Applique toutes les règles de nettoyage et normalisation
    """
    # 1. Validation du Schéma : Vérifier si les colonnes obligatoires existent 
    required_columns = ['order_id', 'client_id', 'product_id', 'country', 
                        'order_date', 'quantity', 'unit_price', 'status']
    for col in required_columns:
        if col not in df.columns:
            print(f"Erreur : Colonne manquante {col}. Fichier rejeté.")
            return None

    # 2. Nettoyage des valeurs manquantes 
    # Rejeter si les colonnes clés sont vides
    df = df.dropna(subset=['order_id', 'product_id', 'quantity', 'unit_price', 'status'])
    # Remplacer pays vide par UNKNOWN
    df['country'] = df['country'].fillna('UNKNOWN')

    # 3. Validation des types et formats 
    try:
        df['order_date'] = pd.to_datetime(df['order_date']).dt.date
        df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0).astype(int)
        df['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce').fillna(0.0)
    except Exception as e:
        print(f"Erreur de conversion de type : {e}")

    # Filtrer les valeurs incohérentes (Quantité et Prix > 0)
    df = df[(df['quantity'] > 0) & (df['unit_price'] > 0)]

    # 4. Normalisation des valeurs textuelles
    # Status : PAID, CANCELLED
    df['status'] = df['status'].str.upper().str.strip()
    # Pays : Majuscule et sans espaces
    df['country'] = df['country'].str.upper().str.strip()

    # 5. Suppression des doublons (Basé sur order_id) 
    df = df.drop_duplicates(subset=['order_id'], keep='first')

    # 6. Ajout des métadonnées (Canal et Timestamp)
    if 'website' in file_name:
        df['channel'] = 'website'
    elif 'mobile' in file_name:
        df['channel'] = 'mobile'
    elif 'partner' in file_name:
        df['channel'] = 'partner'
    else:
        df['channel'] = 'unknown'
    
    df['ingestion_timestamp'] = datetime.now()

    return df

def upload_to_bigquery(df):
    """
    Envoie le DataFrame nettoyé vers BigQuery (Table Partitionnée) 
    """
    client = bigquery.Client()
    
    # Configuration du job d'insertion
    job_config = bigquery.LoadJobConfig(
        # Créer la table si elle n'existe pas, sinon ajouter à la suite
        write_disposition="WRITE_APPEND",
        # Définition du partitionnement par jour sur la colonne order_date 
        time_partitioning=bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="order_date", 
        ),
        autodetect=True,
    )

    try:
        job = client.load_table_from_dataframe(df, TABLE_REF, job_config=job_config)
        job.result()  # Attend la fin du chargement
        print(f"✓ {len(df)} lignes insérées avec succès dans {TABLE_REF}")
    except Exception as e:
        print(f"✗ Erreur lors de l'insertion BigQuery : {e}")

def process_file(file_path):
    """
    Fonction principale d'extraction
    """
    print(f"Traitement du fichier : {file_path}")
    
    # Extraction : Lecture du CSV
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier : {e}")
        return

    # Nettoyage et Normalisation
    df_clean = clean_and_normalize(df, os.path.basename(file_path))

    # Insertion
    if df_clean is not None and not df_clean.empty:
        upload_to_bigquery(df_clean)
    else:
        print("Aucune donnée valide à insérer.")

# --- EXECUTION ---
if __name__ == "__main__":
    # Exemple pour un fichier local généré par tes camarades
    # Tu peux boucler sur les dossiers générés : globalshop-raw/2025-04-01/...
    test_file = "globalshop-raw/2025-04-01/mobile_orders.csv"
    if os.path.exists(test_file):
        process_file(test_file)
    else:
        print("Fichier de test non trouvé. Lancez d'abord les simulateurs.")