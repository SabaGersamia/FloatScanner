import os
import sys
import time
import signal
from pathlib import Path
import traceback 

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FloatScanner.settings')

import django
django.setup()

from scanner.management.commands.fetch_data import Command as ScannerCommand

def handle_exit(signum, frame):
    """Gracefully shuts down the scanner on Ctrl+C."""
    print("\nShutting down gracefully...")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, handle_exit)
    
    print("====================================")
    print("      Starting FloatScanner       ")
    print("====================================")
    
    retry_count = 0
    max_retries = 3
    
    while retry_count < max_retries:
        try:
            print("\n[SYSTEM] Starting continuous scanner...")
            scanner = ScannerCommand()
            
            scanner.handle(target_listings=20, continuous=True, interval=60, verbosity=1)
            break 
            
        except Exception as e:
            retry_count += 1
            print(f"[ERROR] Attempt {retry_count}/{max_retries}: {str(e)}")
            traceback.print_exc() 
            
            if retry_count < max_retries:
                print(f"Retrying in {10 * retry_count} seconds...")
                time.sleep(10 * retry_count) 
            else:
                print("[FATAL] Maximum retries reached. Exiting.")
                sys.exit(1)

if __name__ == "__main__":
    main()