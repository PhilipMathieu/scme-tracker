#!/usr/bin/env python
"""
Script to run the CSV scraper with configured URL.
"""
import asyncio
import csv
import datetime
import os
import sys

from csv_scraper import scrape_and_download
from config import QUORUM_URL, DEFAULT_BROWSER, DEFAULT_TIMEOUT

async def main():
    """Run the scraper with the configured URL."""
    print(f"Starting CSV scraper at {datetime.datetime.now().isoformat()}")
    print(f"Using URL: {QUORUM_URL}")
    
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Create archive directory
    archive_dir = "archive"
    os.makedirs(archive_dir, exist_ok=True)
    
    # Run the scraper
    success, error = await scrape_and_download(
        QUORUM_URL,
        browser_type=DEFAULT_BROWSER,
        download_timeout=DEFAULT_TIMEOUT,
        headless=True  # Run in headless mode for automation
    )
    
    if success:
        # Get the filename (should be maine-2025-priority-bills.csv)
        filename = os.path.basename(QUORUM_URL.rstrip('/')) + ".csv"
        if not os.path.exists(filename):
            # Try to find the downloaded file
            downloaded_files = [f for f in os.listdir() if f.endswith('.csv') and os.path.isfile(f)]
            if downloaded_files:
                filename = downloaded_files[0]
            else:
                print("Error: Cannot find downloaded CSV file")
                sys.exit(1)
        
        # Log the row count
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            row_count = sum(1 for _ in reader)
        print(f"Downloaded CSV with {row_count} rows")
        
        # Create a date-stamped copy in the archive directory
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        archive_filename = f"{os.path.splitext(filename)[0]}_{today}.csv"
        archive_path = os.path.join(archive_dir, archive_filename)
        
        # Copy to archive
        with open(filename, 'rb') as src_file:
            content = src_file.read()
        
        with open(archive_path, 'wb') as dest_file:
            dest_file.write(content)
        
        print(f"Archived CSV to {archive_path}")
        print("CSV download completed successfully!")
        return 0
    else:
        print(f"Failed to download CSV: {error}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)