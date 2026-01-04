"""
GlobalShop - Website Sales Data Simulator
Generates daily CSV files with order data from the website channel
Order IDs are prefixed with 'WEB-' to identify the source
"""

import csv
import random
from datetime import datetime, timedelta
import os
from pathlib import Path

# Configuration
ORDERS_PER_DAY = 200000  # Website generates 200k orders per day
NUM_DAYS = 5
START_DATE = datetime(2025, 4, 1)
OUTPUT_BASE_PATH = "globalshop-raw"  # Local simulation of GCS bucket

# Data generators
COUNTRIES = ['FR', 'DE', 'ES', 'IT', 'UK', 'US', 'CA', 'BE', 'NL', 'CH']
PRODUCT_IDS = [f'PROD-{i:05d}' for i in range(1, 1001)]  # 1000 different products
STATUS_OPTIONS = ['PAID', 'CANCELLED']
STATUS_WEIGHTS = [0.92, 0.08]  # 92% PAID, 8% CANCELLED

def generate_order_id(day_counter, order_num):
    """Generate unique order ID with WEB prefix"""
    timestamp = int(datetime.now().timestamp() * 1000) % 1000000
    return f'WEB-{day_counter:03d}{order_num:06d}{timestamp:06d}'

def generate_client_id():
    """Generate random client ID"""
    return f'CLIENT-{random.randint(1, 50000):06d}'

def generate_order(day_counter, order_num, order_date):
    """Generate a single order record"""
    return {
        'order_id': generate_order_id(day_counter, order_num),
        'client_id': generate_client_id(),
        'product_id': random.choice(PRODUCT_IDS),
        'country': random.choice(COUNTRIES),
        'order_date': order_date.strftime('%Y-%m-%d'),
        'quantity': random.randint(1, 10),
        'unit_price': round(random.uniform(9.99, 999.99), 2),
        'status': random.choices(STATUS_OPTIONS, weights=STATUS_WEIGHTS)[0]
    }

def create_daily_csv(day_counter, order_date):
    """Create CSV file for a specific day"""
    # Create directory structure: globalshop-raw/YYYY-MM-DD/
    date_str = order_date.strftime('%Y-%m-%d')
    output_dir = Path(OUTPUT_BASE_PATH) / date_str
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / 'website_orders.csv'
    
    print(f"Generating {ORDERS_PER_DAY:,} website orders for {date_str}...")
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['order_id', 'client_id', 'product_id', 'country', 
                     'order_date', 'quantity', 'unit_price', 'status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        # Generate orders in batches for memory efficiency
        batch_size = 10000
        for i in range(0, ORDERS_PER_DAY, batch_size):
            batch_orders = [
                generate_order(day_counter, j, order_date) 
                for j in range(i, min(i + batch_size, ORDERS_PER_DAY))
            ]
            writer.writerows(batch_orders)
            
            # Progress indicator
            if (i + batch_size) % 50000 == 0:
                print(f"  Progress: {i + batch_size:,}/{ORDERS_PER_DAY:,} orders generated")
    
    print(f"✓ Created: {output_file} ({ORDERS_PER_DAY:,} orders)")
    return output_file

def main():
    """Main execution function"""
    print("=" * 70)
    print("GlobalShop Website Sales Data Generator")
    print("=" * 70)
    print(f"Configuration:")
    print(f"  - Orders per day: {ORDERS_PER_DAY:,}")
    print(f"  - Number of days: {NUM_DAYS}")
    print(f"  - Start date: {START_DATE.strftime('%Y-%m-%d')}")
    print(f"  - Output path: {OUTPUT_BASE_PATH}/")
    print("=" * 70)
    
    total_orders = 0
    
    for day in range(NUM_DAYS):
        current_date = START_DATE + timedelta(days=day)
        create_daily_csv(day + 1, current_date)
        total_orders += ORDERS_PER_DAY
        print()
    
    print("=" * 70)
    print(f"✓ COMPLETE: Generated {total_orders:,} total website orders")
    print(f"✓ Data stored in: {OUTPUT_BASE_PATH}/")
    print("=" * 70)

if __name__ == "__main__":
    main()
