#!/usr/bin/env python3
"""
Complete 2024-25 Season Backtest Runner
Imports data and runs comprehensive backtesting
"""

import subprocess
import sys
import os
import time
from datetime import datetime

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"{description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"{description} failed")
        print(f"Error: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False

def main():
    """Main function to run complete 2024-25 backtest"""
    print("NBA 2024-25 Season Backtest Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Import 2024-25 season data from Basketball Reference
    print("\nSTEP 1: Importing 2024-25 Season Data from Basketball Reference")
    if not run_command("python import_manual_2024_25_games.py", "Import real 2024-25 season data"):
        print("Failed to import 2024-25 season data. Exiting.")
        return
    
    # Wait a moment for database operations to complete
    print("\nWaiting for database operations to complete...")
    time.sleep(3)
    
    # Step 2: Run backtest
    print("\nSTEP 2: Running 2024-25 Season Backtest")
    if not run_command("python backtest_2024_25_season.py", "Run 2024-25 season backtest"):
        print("Failed to run backtest. Check the logs above.")
        return
    
    # Step 3: Auto-calibrate model
    print("\nSTEP 3: Auto-Calibrating Model Based on Backtest Results")
    if not run_command("python auto_calibrate_model.py", "Auto-calibrate prediction model"):
        print("Warning: Auto-calibration failed. Model will use previous settings.")
    
    # Step 4: Summary
    print("\n" + "=" * 60)
    print("2024-25 Season Backtest Suite Complete!")
    print("=" * 60)
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nResults:")
    print("   - Backtest results saved to JSON file")
    print("   - Model calibration saved to model_calibration.json")
    print("\nYou can also run individual scripts:")
    print("   - python import_manual_2024_25_games.py - Import real season data")
    print("   - python backtest_2024_25_season.py - Run backtest only")
    print("   - python auto_calibrate_model.py - Calibrate model from backtest")
    print("   - python apply_model_calibration.py - Test calibration adjustments")

if __name__ == "__main__":
    main()
