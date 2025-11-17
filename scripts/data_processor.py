"""
Data Processor for Cricsheet JSON Files
Transforms JSON match data into structured Pandas DataFrames
"""

import os
import json
import zipfile
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional


class CricsheetDataProcessor:
    """Process Cricsheet JSON files into structured DataFrames"""
    
    def __init__(self, raw_data_dir="data/raw", processed_data_dir="data/processed"):
        """
        Initialize the data processor
        
        Args:
            raw_data_dir (str): Directory containing raw JSON/ZIP files
            processed_data_dir (str): Directory to save processed CSV files
        """
        self.raw_data_dir = raw_data_dir
        self.processed_data_dir = processed_data_dir
        os.makedirs(processed_data_dir, exist_ok=True)
    
    def extract_zip_files(self):
        """Extract all ZIP files in the raw data directory"""
        zip_files = list(Path(self.raw_data_dir).glob("*.zip"))
        
        for zip_file in zip_files:
            print(f"Extracting {zip_file.name}...")
            try:
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(self.raw_data_dir)
                print(f"Successfully extracted {zip_file.name}")
            except Exception as e:
                print(f"Error extracting {zip_file.name}: {e}")
    
    def load_json_file(self, filepath: str) -> Optional[Dict]:
        """
        Load and parse a JSON file
        
        Args:
            filepath (str): Path to JSON file
            
        Returns:
            dict: Parsed JSON data or None if error
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return None
    
    def process_match_data(self, match_data: Dict) -> Dict:
        """
        Extract key information from a match JSON
        
        Args:
            match_data (dict): Raw match JSON data
            
        Returns:
            dict: Processed match information
        """
        try:
            # Extract match metadata
            match_info = {
                'match_id': match_data.get('meta', {}).get('data_version', ''),
                'date': match_data.get('info', {}).get('dates', [None])[0],
                'match_type': match_data.get('info', {}).get('match_type', ''),
                'venue': match_data.get('info', {}).get('venue', ''),
                'city': match_data.get('info', {}).get('city', ''),
                'toss_winner': match_data.get('info', {}).get('toss', {}).get('winner', ''),
                'toss_decision': match_data.get('info', {}).get('toss', {}).get('decision', ''),
                'team1': match_data.get('info', {}).get('teams', [None, None])[0],
                'team2': match_data.get('info', {}).get('teams', [None, None])[1],
                'winner': match_data.get('info', {}).get('outcome', {}).get('winner', ''),
                'result': match_data.get('info', {}).get('outcome', {}).get('result', ''),
                'player_of_match': ', '.join(match_data.get('info', {}).get('player_of_match', [])),
                'umpires': ', '.join([u.get('name', '') for u in match_data.get('info', {}).get('umpires', [])]),
            }
            
            # Extract innings data
            innings_data = []
            if 'innings' in match_data:
                for inning in match_data['innings']:
                    team = inning.get('team', '')
                    for over_data in inning.get('overs', []):
                        over_num = over_data.get('over', 0)
                        for delivery in over_data.get('deliveries', []):
                            ball = list(delivery.keys())[0]
                            ball_data = delivery[ball]
                            
                            innings_data.append({
                                'match_id': match_info['match_id'],
                                'team': team,
                                'over': over_num,
                                'ball': float(ball),
                                'batter': ball_data.get('batter', ''),
                                'bowler': ball_data.get('bowler', ''),
                                'runs_batter': ball_data.get('runs', {}).get('batter', 0),
                                'runs_extras': ball_data.get('runs', {}).get('extras', 0),
                                'runs_total': ball_data.get('runs', {}).get('total', 0),
                                'wicket': 1 if 'wicket' in ball_data else 0,
                                'wicket_kind': ball_data.get('wicket', {}).get('kind', '') if 'wicket' in ball_data else '',
                                'wicket_player_out': ball_data.get('wicket', {}).get('player_out', '') if 'wicket' in ball_data else '',
                            })
            
            return {
                'match_info': match_info,
                'innings_data': innings_data
            }
            
        except Exception as e:
            print(f"Error processing match data: {e}")
            return None
    
    def process_match_type(self, match_type: str) -> tuple:
        """
        Process all JSON files for a specific match type
        
        Args:
            match_type (str): Type of match (test, odi, t20, ipl)
            
        Returns:
            tuple: (matches_df, deliveries_df) DataFrames
        """
        print(f"\nProcessing {match_type.upper()} matches...")
        
        # Find all JSON files for this match type
        json_files = list(Path(self.raw_data_dir).glob(f"**/*{match_type}*.json"))
        
        if not json_files:
            print(f"No JSON files found for {match_type}")
            return None, None
        
        print(f"Found {len(json_files)} JSON files")
        
        matches_list = []
        deliveries_list = []
        
        for i, json_file in enumerate(json_files):
            if (i + 1) % 100 == 0:
                print(f"Processed {i + 1}/{len(json_files)} files...")
            
            match_data = self.load_json_file(str(json_file))
            if match_data:
                processed = self.process_match_data(match_data)
                if processed:
                    matches_list.append(processed['match_info'])
                    deliveries_list.extend(processed['innings_data'])
        
        # Create DataFrames
        matches_df = pd.DataFrame(matches_list)
        deliveries_df = pd.DataFrame(deliveries_list)
        
        print(f"Processed {len(matches_df)} matches and {len(deliveries_df)} deliveries")
        
        return matches_df, deliveries_df
    
    def create_batting_stats(self, deliveries_df: pd.DataFrame) -> pd.DataFrame:
        """Create batting statistics DataFrame"""
        if deliveries_df.empty:
            return pd.DataFrame()
        
        batting_stats = deliveries_df.groupby(['match_id', 'batter']).agg({
            'runs_batter': 'sum',
            'ball': 'count'
        }).reset_index()
        
        batting_stats.columns = ['match_id', 'player', 'runs', 'balls_faced']
        batting_stats['strike_rate'] = (batting_stats['runs'] / batting_stats['balls_faced'] * 100).round(2)
        
        return batting_stats
    
    def create_bowling_stats(self, deliveries_df: pd.DataFrame) -> pd.DataFrame:
        """Create bowling statistics DataFrame"""
        if deliveries_df.empty:
            return pd.DataFrame()
        
        bowling_stats = deliveries_df.groupby(['match_id', 'bowler']).agg({
            'runs_total': 'sum',
            'ball': 'count',
            'wicket': 'sum'
        }).reset_index()
        
        bowling_stats.columns = ['match_id', 'player', 'runs_conceded', 'balls_bowled', 'wickets']
        bowling_stats['overs'] = (bowling_stats['balls_bowled'] / 6).round(2)
        bowling_stats['economy'] = (bowling_stats['runs_conceded'] / bowling_stats['overs']).round(2)
        bowling_stats['economy'] = bowling_stats['economy'].replace([float('inf'), float('-inf')], 0)
        
        return bowling_stats
    
    def save_processed_data(self, match_type: str, matches_df: pd.DataFrame, 
                           deliveries_df: pd.DataFrame, batting_df: pd.DataFrame = None,
                           bowling_df: pd.DataFrame = None):
        """
        Save processed DataFrames to CSV files
        
        Args:
            match_type (str): Type of match
            matches_df (pd.DataFrame): Matches DataFrame
            deliveries_df (pd.DataFrame): Deliveries DataFrame
            batting_df (pd.DataFrame): Batting stats DataFrame
            bowling_df (pd.DataFrame): Bowling stats DataFrame
        """
        if matches_df is not None and not matches_df.empty:
            matches_file = os.path.join(self.processed_data_dir, f"{match_type}_matches.csv")
            matches_df.to_csv(matches_file, index=False)
            print(f"Saved matches data to {matches_file}")
        
        if deliveries_df is not None and not deliveries_df.empty:
            deliveries_file = os.path.join(self.processed_data_dir, f"{match_type}_deliveries.csv")
            deliveries_df.to_csv(deliveries_file, index=False)
            print(f"Saved deliveries data to {deliveries_file}")
        
        if batting_df is not None and not batting_df.empty:
            batting_file = os.path.join(self.processed_data_dir, f"{match_type}_batting.csv")
            batting_df.to_csv(batting_file, index=False)
            print(f"Saved batting stats to {batting_file}")
        
        if bowling_df is not None and not bowling_df.empty:
            bowling_file = os.path.join(self.processed_data_dir, f"{match_type}_bowling.csv")
            bowling_df.to_csv(bowling_file, index=False)
            print(f"Saved bowling stats to {bowling_file}")
    
    def process_all_match_types(self, match_types: List[str] = ["test", "odi", "t20", "ipl"]):
        """
        Process all match types
        
        Args:
            match_types (list): List of match types to process
        """
        print("Extracting ZIP files...")
        self.extract_zip_files()
        
        print("\n" + "="*50)
        print("Processing all match types...")
        print("="*50)
        
        for match_type in match_types:
            matches_df, deliveries_df = self.process_match_type(match_type)
            
            if matches_df is not None and deliveries_df is not None:
                # Create additional statistics
                batting_df = self.create_batting_stats(deliveries_df)
                bowling_df = self.create_bowling_stats(deliveries_df)
                
                # Save processed data
                self.save_processed_data(match_type, matches_df, deliveries_df, batting_df, bowling_df)
        
        print("\n" + "="*50)
        print("Data processing completed!")
        print("="*50)


def main():
    """Main function to run the data processor"""
    processor = CricsheetDataProcessor()
    processor.process_all_match_types(match_types=["test", "odi", "t20", "ipl"])


if __name__ == "__main__":
    main()

