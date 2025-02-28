# SCME Tracker

A tool for scraping and tracking CSV data for policy bill tracking. Automatically downloads and archives legislative bill data from Quorum.

## Setup

1. Install dependencies:
```bash
pip install -e .
playwright install
```

## Usage

### Manual Scraping

Run the scraper with a custom URL:
```bash
python csv-scraper.py URL [--browser {chromium|firefox|webkit}] [--timeout SECONDS] [--no-headless] [--verify-content]
```

Or use the installed script:
```bash
scrape URL [options]
```

Options:
- `--browser {chromium|firefox|webkit}`: Select browser engine (default: chromium)
- `--timeout SECONDS`: Download timeout in seconds (default: 30)
- `--no-headless`: Run browser in visible mode
- `--verify-content`: Verify CSV content and retry in visible mode if needed

Example:
```bash
python csv-scraper.py https://www.quorum.us/spreadsheet/external/JYrGBpZgfQeehlRsrxnv/ --verify-content
```

### Automated Scraping

Run the scraper with the pre-configured URL:
```bash
python run_scraper.py
```

This will:
1. Download the CSV from the URL configured in `config.py`
2. Archive a date-stamped copy to the `archive/` directory

## GitHub Actions Workflow

This repository includes a GitHub Actions workflow that:

1. Runs daily at 2 AM UTC (9 PM EST)
2. Downloads the latest CSV data
3. Archives a date-stamped copy
4. Creates a commit with the changes
5. Uploads the CSV files as workflow artifacts

You can also trigger the workflow manually via the "Actions" tab in GitHub.