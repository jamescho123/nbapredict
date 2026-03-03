"""
Continuous Data Update Runner
Runs the NBA data extraction every 6 hours while the PC remains open.
"""

import time
import logging
from datetime import datetime, timedelta
from weekly_data_update import run_weekly_update

# Configure logging to console and file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("continuous_update.log"),
        logging.StreamHandler()
    ]
)

def run_loop():
    update_interval_hours = 6
    seconds_in_hour = 3600
    
    while True:
        logging.info("Starting scheduled data update...")
        try:
            # Call the existing update orchestrator
            run_weekly_update()
            logging.info("Update cycle finished successfully.")
        except Exception as e:
            logging.error(f"Error during update cycle: {e}")
            logging.info("Will attempt next update regardless.")

        next_run = datetime.now() + timedelta(hours=update_interval_hours)
        logging.info(f"Next update scheduled for: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Countdown sleep to show progress or just sleep
        # Sleeping in chunks allows for easier interruption if needed, 
        # but for a background script, a single sleep is often fine.
        # We'll sleep for the full interval.
        time.sleep(update_interval_hours * seconds_in_hour)

if __name__ == "__main__":
    logging.info("========================================================")
    logging.info("NBA DATA CONTINUOUS UPDATE SERVICE STARTED")
    logging.info(f"Frequency: Every {6} hours")
    logging.info("========================================================")
    run_loop()
