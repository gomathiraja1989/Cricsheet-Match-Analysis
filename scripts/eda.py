"""
Exploratory Data Analysis (EDA) Script
Creates 10 different visualizations using matplotlib, seaborn, and plotly
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
from pathlib import Path


class CricsheetEDA:
    """Perform Exploratory Data Analysis on cricket match data"""
    
    def __init__(self, db_path="database/cricket_matches.db", output_dir="visualizations/eda"):
        """
        Initialize EDA class
        
        Args:
            db_path (str): Path to SQLite database
            output_dir (str): Directory to save visualizations
        """
        self.db_path = db_path
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.conn = None
        
        # Set style
        try:
            plt.style.use('seaborn-v0_8-darkgrid')
        except:
            try:
                plt.style.use('seaborn-darkgrid')
            except:
                plt.style.use('ggplot')
        sns.set_palette("husl")
    
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
    
    def load_data(self, query: str) -> pd.DataFrame:
        """Load data from database"""
        return pd.read_sql_query(query, self.conn)
    
    # Visualization 1: Top 10 Run Scorers (Matplotlib)
    def visualization_1_top_run_scorers(self):
        """Top 10 run scorers across all formats using Matplotlib"""
        query = """
        SELECT player, SUM(runs) as total_runs
        FROM (
            SELECT player, runs FROM test_batting
            UNION ALL
            SELECT player, runs FROM odi_batting
            UNION ALL
            SELECT player, runs FROM t20_batting
            UNION ALL
            SELECT player, runs FROM ipl_batting
        )
        GROUP BY player
        ORDER BY total_runs DESC
        LIMIT 10
        """
        
        df = self.load_data(query)
        
        plt.figure(figsize=(12, 6))
        plt.barh(df['player'], df['total_runs'], color='steelblue')
        plt.xlabel('Total Runs', fontsize=12)
        plt.ylabel('Player', fontsize=12)
        plt.title('Top 10 Run Scorers Across All Formats', fontsize=14, fontweight='bold')
        plt.gca().invert_yaxis()
        
        # Add value labels
        for i, v in enumerate(df['total_runs']):
            plt.text(v + 100, i, f'{v:,}', va='center')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, '1_top_run_scorers.png'), dpi=300, bbox_inches='tight')
        plt.close()
        print("Visualization 1: Top Run Scorers - Saved")
    
    # Visualization 2: Wicket Takers Comparison (Seaborn)
    def visualization_2_wicket_takers(self):
        """Top wicket takers by format using Seaborn"""
        query = """
        SELECT 'Test' as format, player, SUM(wickets) as total_wickets
        FROM test_bowling
        GROUP BY player
        ORDER BY total_wickets DESC
        LIMIT 5
        UNION ALL
        SELECT 'ODI' as format, player, SUM(wickets) as total_wickets
        FROM odi_bowling
        GROUP BY player
        ORDER BY total_wickets DESC
        LIMIT 5
        UNION ALL
        SELECT 'T20' as format, player, SUM(wickets) as total_wickets
        FROM t20_bowling
        GROUP BY player
        ORDER BY total_wickets DESC
        LIMIT 5
        """
        
        df = self.load_data(query)
        
        plt.figure(figsize=(14, 6))
        sns.barplot(data=df, x='format', y='total_wickets', hue='player', palette='Set2')
        plt.xlabel('Format', fontsize=12)
        plt.ylabel('Total Wickets', fontsize=12)
        plt.title('Top Wicket Takers by Format', fontsize=14, fontweight='bold')
        plt.legend(title='Player', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, '2_wicket_takers.png'), dpi=300, bbox_inches='tight')
        plt.close()
        print("Visualization 2: Wicket Takers - Saved")
    
    # Visualization 3: Match Distribution by Year (Plotly)
    def visualization_3_matches_by_year(self):
        """Matches played per year using Plotly"""
        query = """
        SELECT SUBSTR(date, 1, 4) as year, COUNT(*) as matches
        FROM odi_matches
        WHERE date IS NOT NULL
        GROUP BY SUBSTR(date, 1, 4)
        ORDER BY year
        """
        
        df = self.load_data(query)
        
        fig = px.line(df, x='year', y='matches', 
                     title='ODI Matches Played Per Year',
                     markers=True)
        fig.update_layout(
            xaxis_title='Year',
            yaxis_title='Number of Matches',
            template='plotly_white',
            height=500
        )
        fig.write_html(os.path.join(self.output_dir, '3_matches_by_year.html'))
        print("Visualization 3: Matches by Year - Saved")
    
    # Visualization 4: Team Win Percentage (Matplotlib)
    def visualization_4_team_win_percentage(self):
        """Team win percentage in ODI matches"""
        query = """
        SELECT 
            team,
            COUNT(*) as total_matches,
            SUM(CASE WHEN winner = team THEN 1 ELSE 0 END) as wins,
            ROUND(CAST(SUM(CASE WHEN winner = team THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 2) as win_percentage
        FROM (
            SELECT team1 as team, winner FROM odi_matches
            UNION ALL
            SELECT team2 as team, winner FROM odi_matches
        )
        GROUP BY team
        HAVING total_matches >= 20
        ORDER BY win_percentage DESC
        LIMIT 10
        """
        
        df = self.load_data(query)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(df['team'], df['win_percentage'], color='coral')
        ax.set_xlabel('Team', fontsize=12)
        ax.set_ylabel('Win Percentage (%)', fontsize=12)
        ax.set_title('Top 10 Teams by Win Percentage (ODI)', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 100)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%', ha='center', va='bottom')
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, '4_team_win_percentage.png'), dpi=300, bbox_inches='tight')
        plt.close()
        print("Visualization 4: Team Win Percentage - Saved")
    
    # Visualization 5: Strike Rate vs Average (Seaborn Scatter)
    def visualization_5_strike_rate_vs_avg(self):
        """Strike rate vs batting average for T20 players"""
        query = """
        SELECT 
            player,
            SUM(runs) as total_runs,
            SUM(balls_faced) as total_balls,
            COUNT(DISTINCT match_id) as matches,
            ROUND(CAST(SUM(runs) AS FLOAT) / SUM(balls_faced) * 100, 2) as strike_rate,
            ROUND(AVG(runs), 2) as avg_runs
        FROM t20_batting
        GROUP BY player
        HAVING total_runs >= 500 AND matches >= 10
        """
        
        df = self.load_data(query)
        
        plt.figure(figsize=(12, 8))
        sns.scatterplot(data=df, x='avg_runs', y='strike_rate', 
                       size='total_runs', hue='matches', 
                       palette='viridis', sizes=(50, 500))
        plt.xlabel('Average Runs per Match', fontsize=12)
        plt.ylabel('Strike Rate', fontsize=12)
        plt.title('T20 Players: Strike Rate vs Average Runs (Min 500 runs)', 
                 fontsize=14, fontweight='bold')
        plt.legend(title='Matches', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, '5_strike_rate_vs_avg.png'), dpi=300, bbox_inches='tight')
        plt.close()
        print("Visualization 5: Strike Rate vs Average - Saved")
    
    # Visualization 6: Economy Rate Distribution (Seaborn)
    def visualization_6_economy_distribution(self):
        """Distribution of economy rates for IPL bowlers"""
        query = """
        SELECT economy
        FROM ipl_bowling
        WHERE economy > 0 AND economy < 20
        """
        
        df = self.load_data(query)
        
        plt.figure(figsize=(12, 6))
        sns.histplot(data=df, x='economy', bins=30, kde=True, color='skyblue')
        plt.xlabel('Economy Rate', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.title('Distribution of Economy Rates in IPL', fontsize=14, fontweight='bold')
        plt.axvline(df['economy'].mean(), color='red', linestyle='--', 
                    label=f'Mean: {df["economy"].mean():.2f}')
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, '6_economy_distribution.png'), dpi=300, bbox_inches='tight')
        plt.close()
        print("Visualization 6: Economy Distribution - Saved")
    
    # Visualization 7: Centuries by Format (Plotly)
    def visualization_7_centuries_by_format(self):
        """Number of centuries by format using Plotly"""
        query = """
        SELECT 'Test' as format, COUNT(*) as centuries
        FROM test_batting WHERE runs >= 100
        UNION ALL
        SELECT 'ODI' as format, COUNT(*) as centuries
        FROM odi_batting WHERE runs >= 100
        UNION ALL
        SELECT 'T20' as format, COUNT(*) as centuries
        FROM t20_batting WHERE runs >= 100
        UNION ALL
        SELECT 'IPL' as format, COUNT(*) as centuries
        FROM ipl_batting WHERE runs >= 100
        """
        
        df = self.load_data(query)
        
        fig = px.pie(df, values='centuries', names='format',
                    title='Centuries Distribution Across Formats',
                    color_discrete_sequence=px.colors.qualitative.Set3)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.write_html(os.path.join(self.output_dir, '7_centuries_by_format.html'))
        print("Visualization 7: Centuries by Format - Saved")
    
    # Visualization 8: Venue Analysis (Matplotlib)
    def visualization_8_top_venues(self):
        """Top venues by number of matches"""
        query = """
        SELECT venue, COUNT(*) as matches
        FROM odi_matches
        WHERE venue IS NOT NULL AND venue != ''
        GROUP BY venue
        ORDER BY matches DESC
        LIMIT 15
        """
        
        df = self.load_data(query)
        
        plt.figure(figsize=(14, 8))
        plt.barh(df['venue'], df['matches'], color='teal')
        plt.xlabel('Number of Matches', fontsize=12)
        plt.ylabel('Venue', fontsize=12)
        plt.title('Top 15 Venues by Number of ODI Matches', fontsize=14, fontweight='bold')
        plt.gca().invert_yaxis()
        
        # Add value labels
        for i, v in enumerate(df['matches']):
            plt.text(v + 1, i, f'{v}', va='center')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, '8_top_venues.png'), dpi=300, bbox_inches='tight')
        plt.close()
        print("Visualization 8: Top Venues - Saved")
    
    # Visualization 9: Player Performance Heatmap (Seaborn)
    def visualization_9_performance_heatmap(self):
        """Heatmap of top players' performance metrics"""
        query = """
        SELECT 
            player,
            SUM(runs) as total_runs,
            COUNT(DISTINCT match_id) as matches,
            ROUND(AVG(runs), 2) as avg_runs,
            MAX(runs) as highest_score
        FROM odi_batting
        GROUP BY player
        HAVING total_runs >= 2000
        ORDER BY total_runs DESC
        LIMIT 15
        """
        
        df = self.load_data(query)
        
        # Prepare data for heatmap
        heatmap_data = df[['player', 'total_runs', 'matches', 'avg_runs', 'highest_score']].set_index('player')
        heatmap_data_normalized = (heatmap_data - heatmap_data.min()) / (heatmap_data.max() - heatmap_data.min())
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(heatmap_data_normalized.T, annot=False, cmap='YlOrRd', 
                   cbar_kws={'label': 'Normalized Value'}, fmt='.2f')
        plt.xlabel('Player', fontsize=12)
        plt.ylabel('Metric', fontsize=12)
        plt.title('Top ODI Batsmen Performance Heatmap', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, '9_performance_heatmap.png'), dpi=300, bbox_inches='tight')
        plt.close()
        print("Visualization 9: Performance Heatmap - Saved")
    
    # Visualization 10: Interactive Dashboard (Plotly)
    def visualization_10_interactive_dashboard(self):
        """Interactive dashboard with multiple metrics"""
        # Get data for multiple metrics
        query1 = """
        SELECT 'Test' as format, COUNT(DISTINCT match_id) as matches
        FROM test_matches
        UNION ALL
        SELECT 'ODI' as format, COUNT(DISTINCT match_id) as matches
        FROM odi_matches
        UNION ALL
        SELECT 'T20' as format, COUNT(DISTINCT match_id) as matches
        FROM t20_matches
        UNION ALL
        SELECT 'IPL' as format, COUNT(DISTINCT match_id) as matches
        FROM ipl_matches
        """
        
        df = self.load_data(query1)
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Matches by Format', 'Top Run Scorers', 
                           'Top Wicket Takers', 'Format Comparison'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "pie"}]]
        )
        
        # Subplot 1: Matches by format
        fig.add_trace(
            go.Bar(x=df['format'], y=df['matches'], name='Matches'),
            row=1, col=1
        )
        
        # Subplot 2: Top run scorers
        query2 = """
        SELECT player, SUM(runs) as total_runs
        FROM odi_batting
        GROUP BY player
        ORDER BY total_runs DESC
        LIMIT 10
        """
        df2 = self.load_data(query2)
        fig.add_trace(
            go.Bar(x=df2['player'], y=df2['total_runs'], name='Runs'),
            row=1, col=2
        )
        
        # Subplot 3: Top wicket takers
        query3 = """
        SELECT player, SUM(wickets) as total_wickets
        FROM odi_bowling
        GROUP BY player
        ORDER BY total_wickets DESC
        LIMIT 10
        """
        df3 = self.load_data(query3)
        fig.add_trace(
            go.Bar(x=df3['player'], y=df3['total_wickets'], name='Wickets'),
            row=2, col=1
        )
        
        # Subplot 4: Format comparison
        fig.add_trace(
            go.Pie(labels=df['format'], values=df['matches'], name='Format'),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            title_text="Cricket Data Analysis Dashboard",
            showlegend=False
        )
        
        fig.write_html(os.path.join(self.output_dir, '10_interactive_dashboard.html'))
        print("Visualization 10: Interactive Dashboard - Saved")
    
    def generate_all_visualizations(self):
        """Generate all 10 visualizations"""
        print("="*50)
        print("Generating EDA Visualizations...")
        print("="*50)
        
        try:
            self.connect()
            
            self.visualization_1_top_run_scorers()
            self.visualization_2_wicket_takers()
            self.visualization_3_matches_by_year()
            self.visualization_4_team_win_percentage()
            self.visualization_5_strike_rate_vs_avg()
            self.visualization_6_economy_distribution()
            self.visualization_7_centuries_by_format()
            self.visualization_8_top_venues()
            self.visualization_9_performance_heatmap()
            self.visualization_10_interactive_dashboard()
            
            print("\n" + "="*50)
            print("All visualizations generated successfully!")
            print(f"Output directory: {self.output_dir}")
            print("="*50)
            
        except Exception as e:
            print(f"Error generating visualizations: {e}")
        finally:
            self.close()


def main():
    """Main function"""
    eda = CricsheetEDA()
    eda.generate_all_visualizations()


if __name__ == "__main__":
    main()

