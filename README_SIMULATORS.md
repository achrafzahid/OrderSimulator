# GlobalShop Sales Data Simulators - Part 1

## Vue d'ensemble

Ce projet simule un flux continu de données de commandes pour GlobalShop, une société de e-commerce multi-canaux. Les données sont générées pour trois canaux de vente distincts et stockées dans une structure de Data Lake brut.

## Structure du Projet

### Scripts de Simulation

1. **website_sales.py** - Simulateur du site web
   - Génère **200,000 commandes/jour**
   - Préfixe des order_id: `WEB-`
   - Taux de conversion: 92% PAID, 8% CANCELLED

2. **mobile_sales.py** - Simulateur des applications mobiles
   - Génère **150,000 commandes/jour**
   - Préfixe des order_id: `MOB-`
   - Taux de conversion: 95% PAID, 5% CANCELLED
   - Prix moyens plus bas (utilisateurs mobiles)

3. **partner_sales.py** - Simulateur des partenaires e-commerce
   - Génère **150,000 commandes/jour**
   - Préfixe des order_id: `PTR-`
   - Taux de conversion: 88% PAID, 12% CANCELLED
   - Gamme de prix plus large (inclut bulk orders)

4. **run_all_simulators.py** - Script principal
   - Exécute les trois simulateurs en séquence
   - Affiche un rapport de synthèse

## Format des Données

### Structure CSV

Chaque fichier CSV contient les colonnes suivantes:

```csv
order_id,client_id,product_id,country,order_date,quantity,unit_price,status
```

### Exemple de ligne:
```
WEB-0010000011234567,CLIENT-012345,PROD-00234,FR,2025-04-01,3,49.99,PAID
```

### Explication des champs:

- **order_id**: Identifiant unique avec préfixe source (WEB-/MOB-/PTR-)
- **client_id**: Identifiant client (pool de 50,000 clients)
- **product_id**: Identifiant produit (1,000 produits disponibles)
- **country**: Code pays ISO (10-12 pays par canal)
- **order_date**: Date de la commande (YYYY-MM-DD)
- **quantity**: Quantité commandée (1-15 selon le canal)
- **unit_price**: Prix unitaire en euros
- **status**: Statut de la commande (PAID ou CANCELLED)

## Structure du Data Lake Brut

```
globalshop-raw/
├── 2025-04-01/
│   ├── website_orders.csv
│   ├── mobile_orders.csv
│   └── partner_orders.csv
├── 2025-04-02/
│   ├── website_orders.csv
│   ├── mobile_orders.csv
│   └── partner_orders.csv
├── 2025-04-03/
│   ├── website_orders.csv
│   ├── mobile_orders.csv
│   └── partner_orders.csv
├── 2025-04-04/
│   ├── website_orders.csv
│   ├── mobile_orders.csv
│   └── partner_orders.csv
└── 2025-04-05/
    ├── website_orders.csv
    ├── mobile_orders.csv
    └── partner_orders.csv
```

## Volume de Données Généré

- **Par jour**: 500,000 commandes (200k + 150k + 150k)
- **Total (5 jours)**: 2,500,000 commandes
- **Taille approximative**: ~300-400 MB de données CSV

## Utilisation

### Exécution de tous les simulateurs

```bash
python run_all_simulators.py
```

### Exécution d'un simulateur individuel

```bash
python website_sales.py
python mobile_sales.py
python partner_sales.py
```

## Configuration

Les paramètres peuvent être modifiés dans chaque script:

```python
ORDERS_PER_DAY = 200000  # Nombre de commandes par jour
NUM_DAYS = 5              # Nombre de jours à simuler
START_DATE = datetime(2025, 4, 1)  # Date de début
OUTPUT_BASE_PATH = "globalshop-raw"  # Chemin de sortie
```

## Caractéristiques des Order IDs

Les order_ids sont générés avec un format unique permettant:

1. **Identification de la source** via le préfixe:
   - `WEB-` : Commandes du site web
   - `MOB-` : Commandes des apps mobiles
   - `PTR-` : Commandes des partenaires

2. **Unicité garantie** via la combinaison:
   - Compteur de jour (3 chiffres)
   - Numéro de commande (6 chiffres)
   - Timestamp (6 chiffres)

3. **Exemple**: `WEB-001000123456789`
   - WEB = Source (Website)
   - 001 = Jour 1
   - 000123 = Commande #123
   - 456789 = Timestamp

## Dépendances

Le code utilise uniquement la bibliothèque standard Python:
- csv
- random
- datetime
- pathlib
- os

**Aucune installation de package externe requise!**

## Migration vers Google Cloud Storage

Pour déployer vers GCS, il suffit de:

1. Installer le SDK: `pip install google-cloud-storage`
2. Modifier `OUTPUT_BASE_PATH` dans chaque script
3. Utiliser les fonctions GCS pour l'upload

Exemple de modification:
```python
from google.cloud import storage

def upload_to_gcs(local_file, bucket_name, blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(local_file)
```

## Prochaines Étapes (Part 2)

- Ingestion des données dans BigQuery
- Création du Data Warehouse
- Transformations et analyses
- Dashboard de visualisation

## Notes

- Les données sont générées de manière aléatoire mais réaliste
- Les distributions de pays et statuts varient selon le canal
- Les prix et quantités reflètent les comportements d'achat typiques
- La structure permet une scalabilité facile vers des volumes plus importants
