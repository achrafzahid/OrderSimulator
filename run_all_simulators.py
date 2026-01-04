"""
GlobalShop - Master Script to Run All Sales Simulators
Executes all three sales channel simulators in sequence
"""

import subprocess
import sys
from datetime import datetime

def run_simulator(script_name, description):
    """Run a simulator script and handle errors"""
    print(f"\n{'=' * 70}")
    print(f"Starting: {description}")
    print(f"{'=' * 70}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            check=True,
            capture_output=False,
            text=True
        )
        print(f"\n✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error running {description}")
        print(f"Error: {e}")
        return False
    except FileNotFoundError:
        print(f"\n✗ Error: {script_name} not found")
        return False

def main():
    """Main execution function"""
    start_time = datetime.now()
    
    print("\n" + "=" * 70)
    print(" " * 15 + "GLOBALSHOP DATA GENERATION PIPELINE")
    print("=" * 70)
    print(f"Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    simulators = [
        ('website_sales.py', 'Website Sales Simulator'),
        ('mobile_sales.py', 'Mobile App Sales Simulator'),
        ('partner_sales.py', 'Partner E-commerce Sales Simulator')
    ]
    
    results = []
    for script, description in simulators:
        success = run_simulator(script, description)
        results.append((description, success))
    
    # Summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "=" * 70)
    print(" " * 20 + "EXECUTION SUMMARY")
    print("=" * 70)
    
    for description, success in results:
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{status}: {description}")
    
    print(f"\nTotal execution time: {duration}")
    print(f"Completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Calculate total orders
    successful_count = sum(1 for _, success in results if success)
    if successful_count == 3:
        total_orders = 5 * 500000  # 5 days × 500k orders/day
        print(f"\n✓ Total orders generated: {total_orders:,}")
        print(f"✓ Data structure: globalshop-raw/YYYY-MM-DD/[channel]_orders.csv")
    
    print("=" * 70 + "\n")
    
    # Exit code
    if all(success for _, success in results):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
