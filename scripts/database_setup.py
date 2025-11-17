"""
Database Setup Script for Cricsheet Match Data
Creates SQLite database and tables for Test, ODI, T20, and IPL matches
"""

import os
import sqlite3
from pathlib import Path


class DatabaseSetup:
    """Setup SQLite database and create tables for cricket match data"""
    
    def __init__(self, db_path="database/cricket_matches.db"):
        """
        Initialize database setup
        
        Args:
            db_path (str): Path to SQLite database file
        """
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = None
    
    def connect(self):
        """Connect to SQLite database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        print(f"Connected to database: {self.db_path}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("Database connection closed")
    
    def create_matches_table(self, match_type: str):
        """
        Create matches table for a specific match type
        
        Args:
            match_type (str): Type of match (test, odi, t20, ipl)
        """
        table_name = f"{match_type}_matches"
        
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id TEXT UNIQUE,
            date TEXT,
            match_type TEXT,
            venue TEXT,
            city TEXT,
            toss_winner TEXT,
            toss_decision TEXT,
            team1 TEXT,
            team2 TEXT,
            winner TEXT,
            result TEXT,
            player_of_match TEXT,
            umpires TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        self.conn.execute(create_table_sql)
        print(f"Created table: {table_name}")
    
    def create_deliveries_table(self, match_type: str):
        """
        Create deliveries table for a specific match type
        
        Args:
            match_type (str): Type of match (test, odi, t20, ipl)
        """
        table_name = f"{match_type}_deliveries"
        
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id TEXT,
            team TEXT,
            over INTEGER,
            ball REAL,
            batter TEXT,
            bowler TEXT,
            runs_batter INTEGER DEFAULT 0,
            runs_extras INTEGER DEFAULT 0,
            runs_total INTEGER DEFAULT 0,
            wicket INTEGER DEFAULT 0,
            wicket_kind TEXT,
            wicket_player_out TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (match_id) REFERENCES {match_type}_matches(match_id)
        );
        """
        
        self.conn.execute(create_table_sql)
        
        # Create indexes for better query performance
        self.conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{match_type}_deliveries_match_id ON {table_name}(match_id)")
        self.conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{match_type}_deliveries_batter ON {table_name}(batter)")
        self.conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{match_type}_deliveries_bowler ON {table_name}(bowler)")
        
        print(f"Created table: {table_name}")
    
    def create_batting_stats_table(self, match_type: str):
        """
        Create batting statistics table
        
        Args:
            match_type (str): Type of match (test, odi, t20, ipl)
        """
        table_name = f"{match_type}_batting"
        
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id TEXT,
            player TEXT,
            runs INTEGER DEFAULT 0,
            balls_faced INTEGER DEFAULT 0,
            strike_rate REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (match_id) REFERENCES {match_type}_matches(match_id)
        );
        """
        
        self.conn.execute(create_table_sql)
        self.conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{match_type}_batting_player ON {table_name}(player)")
        self.conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{match_type}_batting_match_id ON {table_name}(match_id)")
        
        print(f"Created table: {table_name}")
    
    def create_bowling_stats_table(self, match_type: str):
        """
        Create bowling statistics table
        
        Args:
            match_type (str): Type of match (test, odi, t20, ipl)
        """
        table_name = f"{match_type}_bowling"
        
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id TEXT,
            player TEXT,
            runs_conceded INTEGER DEFAULT 0,
            balls_bowled INTEGER DEFAULT 0,
            overs REAL,
            wickets INTEGER DEFAULT 0,
            economy REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (match_id) REFERENCES {match_type}_matches(match_id)
        );
        """
        
        self.conn.execute(create_table_sql)
        self.conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{match_type}_bowling_player ON {table_name}(player)")
        self.conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{match_type}_bowling_match_id ON {table_name}(match_id)")
        
        print(f"Created table: {table_name}")
    
    def create_all_tables(self, match_types: list = ["test", "odi", "t20", "ipl"]):
        """
        Create all tables for all match types
        
        Args:
            match_types (list): List of match types
        """
        print("="*50)
        print("Creating database tables...")
        print("="*50)
        
        for match_type in match_types:
            print(f"\nCreating tables for {match_type.upper()} matches...")
            self.create_matches_table(match_type)
            self.create_deliveries_table(match_type)
            self.create_batting_stats_table(match_type)
            self.create_bowling_stats_table(match_type)
        
        self.conn.commit()
        print("\n" + "="*50)
        print("All tables created successfully!")
        print("="*50)
    
    def get_table_info(self):
        """Display information about all tables in the database"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("\n" + "="*50)
        print("Database Tables:")
        print("="*50)
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"{table_name}: {count} rows")
        print("="*50)


def main():
    """Main function to set up the database"""
    db_setup = DatabaseSetup()
    
    try:
        db_setup.connect()
        db_setup.create_all_tables()
        db_setup.get_table_info()
    except Exception as e:
        print(f"Error setting up database: {e}")
    finally:
        db_setup.close()


if __name__ == "__main__":
    main()

