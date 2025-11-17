"""
Data Loader Script
Loads processed CSV data into SQLite database
"""

import os
import pandas as pd
import sqlite3
from pathlib import Path


class DataLoader:
    """Load processed data into SQLite database"""
    
    def __init__(self, db_path="database/cricket_matches.db", processed_data_dir="data/processed"):
        """
        Initialize data loader
        
        Args:
            db_path (str): Path to SQLite database
            processed_data_dir (str): Directory containing processed CSV files
        """
        self.db_path = db_path
        self.processed_data_dir = processed_data_dir
        self.conn = None
    
    def connect(self):
        """Connect to SQLite database"""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database not found: {self.db_path}. Please run database_setup.py first.")
        
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        print(f"Connected to database: {self.db_path}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("Database connection closed")
    
    def load_csv_to_table(self, csv_file: str, table_name: str, if_exists: str = "replace"):
        """
        Load CSV file into database table
        
        Args:
            csv_file (str): Path to CSV file
            table_name (str): Target table name
            if_exists (str): What to do if table exists ('replace', 'append', 'fail')
        """
        if not os.path.exists(csv_file):
            print(f"CSV file not found: {csv_file}")
            return False
        
        try:
            print(f"Loading {csv_file} into {table_name}...")
            df = pd.read_csv(csv_file)
            
            if df.empty:
                print(f"Warning: {csv_file} is empty")
                return False
            
            # Clean column names (remove spaces, special characters)
            df.columns = df.columns.str.strip().str.replace(' ', '_').str.lower()
            
            # Load data into database
            df.to_sql(table_name, self.conn, if_exists=if_exists, index=False)
            
            # Get row count
            cursor = self.conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            
            print(f"Successfully loaded {count} rows into {table_name}")
            return True
            
        except Exception as e:
            print(f"Error loading {csv_file} into {table_name}: {e}")
            return False
    
    def load_match_type_data(self, match_type: str, if_exists: str = "replace"):
        """
        Load all data files for a specific match type
        
        Args:
            match_type (str): Type of match (test, odi, t20, ipl)
            if_exists (str): What to do if table exists
        """
        print(f"\n{'='*50}")
        print(f"Loading {match_type.upper()} match data...")
        print(f"{'='*50}")
        
        # Load matches
        matches_file = os.path.join(self.processed_data_dir, f"{match_type}_matches.csv")
        if os.path.exists(matches_file):
            self.load_csv_to_table(matches_file, f"{match_type}_matches", if_exists)
        
        # Load deliveries
        deliveries_file = os.path.join(self.processed_data_dir, f"{match_type}_deliveries.csv")
        if os.path.exists(deliveries_file):
            self.load_csv_to_table(deliveries_file, f"{match_type}_deliveries", if_exists)
        
        # Load batting stats
        batting_file = os.path.join(self.processed_data_dir, f"{match_type}_batting.csv")
        if os.path.exists(batting_file):
            self.load_csv_to_table(batting_file, f"{match_type}_batting", if_exists)
        
        # Load bowling stats
        bowling_file = os.path.join(self.processed_data_dir, f"{match_type}_bowling.csv")
        if os.path.exists(bowling_file):
            self.load_csv_to_table(bowling_file, f"{match_type}_bowling", if_exists)
    
    def load_all_match_types(self, match_types: list = ["test", "odi", "t20", "ipl"], if_exists: str = "replace"):
        """
        Load data for all match types
        
        Args:
            match_types (list): List of match types to load
            if_exists (str): What to do if table exists
        """
        print("\n" + "="*50)
        print("Loading all match data into database...")
        print("="*50)
        
        for match_type in match_types:
            self.load_match_type_data(match_type, if_exists)
        
        self.conn.commit()
        print("\n" + "="*50)
        print("Data loading completed!")
        print("="*50)
    
    def verify_data(self):
        """Verify loaded data by displaying row counts"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("\n" + "="*50)
        print("Data Verification - Row Counts:")
        print("="*50)
        
        total_rows = 0
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            total_rows += count
            print(f"{table_name}: {count:,} rows")
        
        print(f"\nTotal rows across all tables: {total_rows:,}")
        print("="*50)


def main():
    """Main function to load data"""
    loader = DataLoader()
    
    try:
        loader.connect()
        loader.load_all_match_types(match_types=["test", "odi", "t20", "ipl"])
        loader.verify_data()
    except Exception as e:
        print(f"Error loading data: {e}")
    finally:
        loader.close()


if __name__ == "__main__":
    main()

