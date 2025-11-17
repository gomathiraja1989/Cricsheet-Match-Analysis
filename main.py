"""
Main Execution Script for Cricsheet Match Data Analysis Project
Orchestrates the entire data pipeline from scraping to visualization
"""

import os
import sys
import argparse
from pathlib import Path

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from scraper import CricsheetScraper
from data_processor import CricsheetDataProcessor
from database_setup import DatabaseSetup
from data_loader import DataLoader
from sql_queries import SQLQueryExecutor
from eda import CricsheetEDA


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")


def step_1_scrape_data():
    """Step 1: Scrape data from Cricsheet"""
    print_section("STEP 1: Scraping Data from Cricsheet")
    
    scraper = CricsheetScraper(download_dir="data/raw")
    
    # Try scraping from downloads page first (finds actual URLs)
    try:
        print("Attempting to scrape from downloads page...")
        scraper.scrape_from_downloads_page()
    except Exception as e:
        print(f"Error with downloads page method: {e}")
        print("\nTrying alternative URL patterns...")
        # Fallback to trying direct URL patterns
        scraper.scrape_from_direct_urls()
    
    print("\n✓ Data scraping completed!")


def step_2_process_data():
    """Step 2: Process JSON files into DataFrames"""
    print_section("STEP 2: Processing JSON Data")
    
    processor = CricsheetDataProcessor(
        raw_data_dir="data/raw",
        processed_data_dir="data/processed"
    )
    
    processor.process_all_match_types(match_types=["test", "odi", "t20", "ipl"])
    
    print("\n✓ Data processing completed!")


def step_3_setup_database():
    """Step 3: Setup SQLite database and tables"""
    print_section("STEP 3: Setting Up Database")
    
    db_setup = DatabaseSetup(db_path="database/cricket_matches.db")
    
    try:
        db_setup.connect()
        db_setup.create_all_tables(match_types=["test", "odi", "t20", "ipl"])
        db_setup.get_table_info()
        print("\n✓ Database setup completed!")
    except Exception as e:
        print(f"✗ Error setting up database: {e}")
        raise
    finally:
        db_setup.close()


def step_4_load_data():
    """Step 4: Load processed data into database"""
    print_section("STEP 4: Loading Data into Database")
    
    loader = DataLoader(
        db_path="database/cricket_matches.db",
        processed_data_dir="data/processed"
    )
    
    try:
        loader.connect()
        loader.load_all_match_types(match_types=["test", "odi", "t20", "ipl"])
        loader.verify_data()
        print("\n✓ Data loading completed!")
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        raise
    finally:
        loader.close()


def step_5_execute_queries():
    """Step 5: Execute SQL queries"""
    print_section("STEP 5: Executing SQL Queries")
    
    executor = SQLQueryExecutor(
        db_path="database/cricket_matches.db",
        output_dir="sql/results"
    )
    
    try:
        executor.connect()
        executor.execute_all_queries(queries_file="sql/queries.sql")
        print("\n✓ SQL queries execution completed!")
    except Exception as e:
        print(f"✗ Error executing queries: {e}")
        raise
    finally:
        executor.close()


def step_6_generate_visualizations():
    """Step 6: Generate EDA visualizations"""
    print_section("STEP 6: Generating EDA Visualizations")
    
    eda = CricsheetEDA(
        db_path="database/cricket_matches.db",
        output_dir="visualizations/eda"
    )
    
    eda.generate_all_visualizations()
    print("\n✓ EDA visualizations generation completed!")


def run_full_pipeline():
    """Run the complete data pipeline"""
    print("\n" + "="*60)
    print("  CRICSHEET MATCH DATA ANALYSIS - FULL PIPELINE")
    print("="*60)
    
    try:
        # Step 1: Scrape data
        step_1_scrape_data()
        
        # Step 2: Process data
        step_2_process_data()
        
        # Step 3: Setup database
        step_3_setup_database()
        
        # Step 4: Load data
        step_4_load_data()
        
        # Step 5: Execute queries
        step_5_execute_queries()
        
        # Step 6: Generate visualizations
        step_6_generate_visualizations()
        
        print("\n" + "="*60)
        print("  ✓ ALL STEPS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nNext Steps:")
        print("1. Review SQL query results in: sql/results/")
        print("2. View EDA visualizations in: visualizations/eda/")
        print("3. Connect Power BI to: database/cricket_matches.db")
        print("4. Create your Power BI dashboard!")
        print("="*60 + "\n")
        
    except Exception as e:
        print("\n" + "="*60)
        print(f"  ✗ PIPELINE FAILED: {e}")
        print("="*60 + "\n")
        sys.exit(1)


def run_individual_step(step_number):
    """Run a specific step of the pipeline"""
    steps = {
        1: ("Scrape Data", step_1_scrape_data),
        2: ("Process Data", step_2_process_data),
        3: ("Setup Database", step_3_setup_database),
        4: ("Load Data", step_4_load_data),
        5: ("Execute Queries", step_5_execute_queries),
        6: ("Generate Visualizations", step_6_generate_visualizations)
    }
    
    if step_number not in steps:
        print(f"Invalid step number. Choose from 1-6")
        return
    
    step_name, step_func = steps[step_number]
    print(f"\nRunning Step {step_number}: {step_name}")
    step_func()


def main():
    """Main function with command-line interface"""
    parser = argparse.ArgumentParser(
        description='Cricsheet Match Data Analysis Pipeline'
    )
    parser.add_argument(
        '--step',
        type=int,
        choices=[1, 2, 3, 4, 5, 6],
        help='Run a specific step (1-6) instead of full pipeline'
    )
    parser.add_argument(
        '--full',
        action='store_true',
        help='Run the complete pipeline (default)'
    )
    
    args = parser.parse_args()
    
    if args.step:
        run_individual_step(args.step)
    else:
        run_full_pipeline()


if __name__ == "__main__":
    main()

