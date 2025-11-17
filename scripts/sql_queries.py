"""
SQL Query Execution Script
Executes the 20 analytical SQL queries and saves results
"""

import os
import sqlite3
import pandas as pd
from pathlib import Path


class SQLQueryExecutor:
    """Execute SQL queries and save results"""
    
    def __init__(self, db_path="database/cricket_matches.db", output_dir="sql/results"):
        """
        Initialize query executor
        
        Args:
            db_path (str): Path to SQLite database
            output_dir (str): Directory to save query results
        """
        self.db_path = db_path
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.conn = None
    
    def connect(self):
        """Connect to database"""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database not found: {self.db_path}")
        
        self.conn = sqlite3.connect(self.db_path)
        print(f"Connected to database: {self.db_path}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def execute_query(self, query: str, query_number: int):
        """
        Execute a SQL query and save results
        
        Args:
            query (str): SQL query to execute
            query_number (int): Query number for naming
        """
        try:
            df = pd.read_sql_query(query, self.conn)
            
            # Save to CSV
            output_file = os.path.join(self.output_dir, f"query_{query_number:02d}_results.csv")
            df.to_csv(output_file, index=False)
            
            print(f"Query {query_number}: Executed successfully - {len(df)} rows")
            return df
            
        except Exception as e:
            print(f"Query {query_number}: Error - {e}")
            return None
    
    def execute_all_queries(self, queries_file="sql/queries.sql"):
        """
        Execute all queries from SQL file
        
        Args:
            queries_file (str): Path to SQL file
        """
        if not os.path.exists(queries_file):
            print(f"SQL file not found: {queries_file}")
            return
        
        print("="*50)
        print("Executing SQL Queries...")
        print("="*50)
        
        with open(queries_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split queries by -- Query pattern
        queries = []
        current_query = ""
        
        for line in content.split('\n'):
            if line.strip().startswith('-- Query'):
                if current_query.strip():
                    queries.append(current_query.strip())
                current_query = ""
            elif not line.strip().startswith('--') or line.strip() == '':
                current_query += line + '\n'
        
        if current_query.strip():
            queries.append(current_query.strip())
        
        # Execute each query
        for i, query in enumerate(queries, 1):
            if query.strip():
                self.execute_query(query, i)
        
        print("\n" + "="*50)
        print("All queries executed!")
        print("="*50)


def main():
    """Main function"""
    executor = SQLQueryExecutor()
    
    try:
        executor.connect()
        executor.execute_all_queries()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        executor.close()


if __name__ == "__main__":
    main()

