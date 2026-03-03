#!/usr/bin/env python3
"""
Complete Real 2024-25 Season Backtest Runner
Imports real season data and runs comprehensive backtesting
"""

import subprocess
import sys
import os
import time
from datetime import datetime

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False

def main():
    """Main function to run complete real 2024-25 backtest"""
    print("🏀 NBA Real 2024-25 Season Backtest Suite")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Import real 2024-25 season data
    print("\n📥 STEP 1: Importing Real 2024-25 Season Data")
    print("   (Including completed games and actual results)")
    if not run_command("python import_real_2024_25_season.py", "Import real 2024-25 season data"):
        print("❌ Failed to import real 2024-25 season data. Exiting.")
        return
    
    # Wait a moment for database operations to complete
    print("\n⏳ Waiting for database operations to complete...")
    time.sleep(3)
    
    # Step 2: Run backtest on real data
    print("\n🧪 STEP 2: Running Backtest on Real 2024-25 Season Data")
    print("   (Testing predictions against actual game results)")
    if not run_command("python backtest_real_2024_25.py", "Run real 2024-25 season backtest"):
        print("❌ Failed to run backtest. Check the logs above.")
        return
    
    # Step 3: Summary
    print("\n" + "=" * 60)
    print("🎉 Real 2024-25 Season Backtest Suite Complete!")
    print("=" * 60)
    print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n📊 Check the generated JSON files for detailed results")
    print("💡 You can also run individual scripts:")
    print("   • python import_real_2024_25_season.py - Import real season data")
    print("   • python backtest_real_2024_25.py - Run backtest on real data")

if __name__ == "__main__":
    main()
