# SCME Tracker Development Guide

## Common Commands
- Setup: `pip install -e . && playwright install`
- Run scraper:
  - Manual with URL: `python csv_scraper.py URL [options]` or `scrape URL [options]`
  - Recommended usage: `python csv_scraper.py URL --verify-content`
  - With configured URL: `python run_scraper.py`
- Install dev tools: `pip install pytest black isort mypy ruff`
- Lint: `ruff check . && black --check .`
- Format: `black . && isort .`
- Type check: `mypy csv_scraper.py run_scraper.py`

## Configuration
- URL settings: Edit `config.py` to change the data source URL
- GitHub workflow: `.github/workflows/daily-scraper.yml` runs daily at 2 AM UTC

## Code Style Guidelines
- **Imports**: Group standard lib, third-party, and project imports with a blank line between groups
- **Formatting**: Use Black with default settings (line length 88)
- **Types**: Use type annotations for all function parameters and return values
- **Docstrings**: Use NumPy style docstrings with Parameters/Returns sections
- **Naming**: 
  - Functions/variables: snake_case
  - Classes: PascalCase
  - Modules: snake_case (e.g., csv_scraper.py not csv-scraper.py)
- **Error handling**: Use try/except blocks with specific exceptions
- **Async**: Use asyncio for async operations with proper await syntax

## Project Structure
- `csv_scraper.py`: Main scraper script
- `run_scraper.py`: Automated script using config
- `config.py`: URL and settings configuration
- `archive/`: Directory for dated CSV backups (contains dated CSV files)
- `downloads/`: Temporary directory for downloaded files
- `.github/workflows/`: Contains GitHub Actions automation

## GitHub Workflow
- The `daily-scraper.yml` workflow:
  - Runs automatically at 2 AM UTC daily
  - Can be triggered manually from GitHub UI
  - Downloads latest CSV data and archives it
  - Commits changes back to the repository
  - Uploads CSVs as artifacts for 90 days