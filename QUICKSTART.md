# Quick Start Guide

## Installation

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install ChromeDriver** (for Selenium):
   - The script uses `webdriver-manager` which automatically downloads ChromeDriver
   - Alternatively, download from: https://chromedriver.chromium.org/

## Running the Project

### Option 1: Run Full Pipeline
```bash
python main.py --full
```

This will execute all steps:
1. Scrape data from Cricsheet
2. Process JSON files
3. Setup SQLite database
4. Load data into database
5. Execute 20 SQL queries
6. Generate 10 EDA visualizations

### Option 2: Run Individual Steps
```bash
# Step 1: Scrape data
python main.py --step 1

# Step 2: Process data
python main.py --step 2

# Step 3: Setup database
python main.py --step 3

# Step 4: Load data
python main.py --step 4

# Step 5: Execute queries
python main.py --step 5

# Step 6: Generate visualizations
python main.py --step 6
```

### Option 3: Run Scripts Individually
```bash
# Scrape data
python scripts/scraper.py

# Process data
python scripts/data_processor.py

# Setup database
python scripts/database_setup.py

# Load data
python scripts/data_loader.py

# Execute queries
python scripts/sql_queries.py

# Generate visualizations
python scripts/eda.py
```

## Project Structure

```
Cricsheet-Match-Analysis/
├── main.py                    # Main execution script
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── QUICKSTART.md             # This file
├── .gitignore                # Git ignore rules
│
├── scripts/                   # Python scripts
│   ├── scraper.py            # Web scraping
│   ├── data_processor.py     # Data transformation
│   ├── database_setup.py     # Database creation
│   ├── data_loader.py        # Data loading
│   ├── sql_queries.py        # Query execution
│   └── eda.py                # Visualizations
│
├── data/                      # Data directory
│   ├── raw/                   # Raw JSON/ZIP files
│   └── processed/             # Processed CSV files
│
├── database/                  # Database files
│   └── cricket_matches.db     # SQLite database
│
├── sql/                       # SQL queries
│   ├── queries.sql           # 20 analytical queries
│   └── results/              # Query results (CSV)
│
├── visualizations/            # Visualizations
│   ├── eda/                  # EDA outputs (PNG/HTML)
│   └── presentation/         # Presentation materials
│
├── powerbi/                   # Power BI files
│   └── README.md             # Power BI setup guide
│
└── docs/                      # Documentation
    └── project_report.md      # Detailed project report
```

## Output Files

After running the pipeline, you'll find:

1. **Database**: `database/cricket_matches.db`
2. **Query Results**: `sql/results/query_01_results.csv` to `query_20_results.csv`
3. **Visualizations**: 
   - PNG files in `visualizations/eda/`
   - HTML files (interactive) in `visualizations/eda/`

## Power BI Setup

1. See `powerbi/README.md` for detailed instructions
2. Connect to `database/cricket_matches.db`
3. Create your dashboard using the SQL queries as reference

## Troubleshooting

### Issue: 404 Error when downloading ZIP files
**Solution**: The scraper now automatically:
1. First tries to find download links from the cricsheet.org downloads page
2. Falls back to trying alternative URL patterns
3. Can download individual JSON files if ZIP files aren't available

If you still get 404 errors:
- The scraper will automatically try alternative methods
- Check your internet connection
- Visit https://cricsheet.org/downloads/ manually to verify the page is accessible
- The scraper can also download individual match JSON files if needed

### Issue: ChromeDriver not found
**Solution**: The script uses `webdriver-manager` which should auto-download. If issues persist, manually install ChromeDriver.

### Issue: Database not found
**Solution**: Run Step 3 (database setup) before Step 4 (data loading).

### Issue: No data files
**Solution**: Run Step 1 (scraping) and Step 2 (processing) first.

### Issue: Import errors
**Solution**: Ensure all dependencies are installed: `pip install -r requirements.txt`

### Issue: Scraper can't find download links
**Solution**: 
- The scraper now uses Selenium to navigate to the downloads page and find actual links
- If headless mode causes issues, the scraper runs in visible mode by default
- Check that Chrome/ChromeDriver is properly installed

## Next Steps

1. Review SQL query results in `sql/results/`
2. View EDA visualizations in `visualizations/eda/`
3. Create Power BI dashboard (see `powerbi/README.md`)
4. Explore the data using custom SQL queries
5. Extend the analysis with additional visualizations

## Support

For detailed information, see:
- `README.md` - Complete project documentation
- `docs/project_report.md` - Detailed methodology and results

