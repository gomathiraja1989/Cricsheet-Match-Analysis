# Power BI Dashboard Setup Guide

1. In Power BI Desktop:
   - Get Data > Python script
   - Use the following script:

```python
import pandas as pd
import sqlite3

# Connect to database
conn = sqlite3.connect(r'D:\path\to\database\cricket_matches.db')

# Load data
odi_matches = pd.read_sql_query("SELECT * FROM odi_matches", conn)
odi_batting = pd.read_sql_query("SELECT * FROM odi_batting", conn)
odi_bowling = pd.read_sql_query("SELECT * FROM odi_bowling", conn)

# Close connection
conn.close()
```

## Recommended Dashboard Components

### 1. Player Performance Dashboard
- Top run scorers (bar chart)
- Top wicket takers (bar chart)
- Strike rate vs average (scatter plot)
- Player performance over time (line chart)

### 2. Team Analysis Dashboard
- Win percentage by team (bar chart)
- Head-to-head records (matrix)
- Team performance by venue (map/bar chart)
- Team statistics summary (cards)

### 3. Match Analysis Dashboard
- Matches by year (line chart)
- Venue analysis (bar chart)
- Toss impact analysis (pie chart)
- Match outcomes (donut chart)

### 4. Format Comparison Dashboard
- Matches by format (pie chart)
- Performance metrics comparison (bar chart)
- Format-wise statistics (table)

## Key Metrics to Include

1. **KPIs (Key Performance Indicators)**:
   - Total matches
   - Total runs scored
   - Total wickets taken
   - Unique players
   - Unique teams

2. **Player Metrics**:
   - Total runs
   - Batting average
   - Strike rate
   - Centuries
   - Half-centuries

3. **Team Metrics**:
   - Win percentage
   - Total wins
   - Total losses
   - Average score

4. **Match Metrics**:
   - Matches by format
   - Matches by venue
   - Matches by year
   - Completed vs abandoned

## Sample Queries for Power BI

You can use the SQL queries from `sql/queries.sql` as a reference for creating Power BI measures and calculated columns.

## Notes

- SQLite database file location: `database/cricket_matches.db`
- Ensure Power BI has read access to the database file
- For large datasets, consider using DirectQuery mode
- Export query results to CSV/Excel for better performance if needed

