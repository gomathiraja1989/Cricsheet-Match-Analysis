# Cricsheet Match Data Analysis

Explore end-to-end cricket analytics by automating data collection from Cricsheet, transforming JSON scorecards into structured SQLite tables, running 20 analytical SQL queries, performing Python-based EDA, and building a Power BI dashboard for stakeholders.

---

## 📑 Table of Contents
1. [Project Overview](#project-overview)
2. [Business Use Cases](#business-use-cases)
3. [Technical Stack](#technical-stack)
4. [Project Structure](#project-structure)
5. [Prerequisites & Installation](#prerequisites--installation)
6. [Data Source](#data-source)
7. [Methodology / Approach](#methodology--approach)
8. [Usage Instructions](#usage-instructions)
9. [Database Schema (SQLite)](#database-schema-sqlite)
10. [SQL Queries Documentation](#sql-queries-documentation)
11. [EDA Visualizations](#eda-visualizations)
12. [Power BI Dashboard](#power-bi-dashboard)
13. [Results & Insights](#results--insights)
---

## Project Overview
- **Domain:** Sports Analytics / Data Analysis  
- **Objective:** Automate scraping of Cricsheet match JSON files (Test, ODI, T20, IPL), process them via Python, store them in SQLite tables, analyze through 20 SQL queries, conduct EDA using matplotlib/seaborn/plotly, and present findings in a Power BI dashboard.  
- **Skills Takeaway:**  
  1. Web scraping with Selenium  
  2. Data processing using Python/Pandas  
  3. SQLite database design & SQL optimization  
  4. Analytical SQL querying  
  5. Visualization with Power BI  
  6. Data preprocessing & cleaning  
  7. Automation workflows

---

## Business Use Cases
1. **Player Performance Analysis:** Track batting/bowling KPIs across formats.  
2. **Team Insights:** Compare teams over seasons and match types.  
3. **Match Outcomes:** Study win/loss trends, margins, toss impact.  
4. **Strategic Decision-Making:** Support analysts/coaches with actionable stats.  
5. **Fan Engagement:** Interactive dashboards for storytelling and fan exploration.

---

## Technical Stack
- **Programming:** Python 3.10+  
- **Automation:** Selenium, ChromeDriver/GeckoDriver  
- **Data Handling:** Pandas, NumPy, json  
- **Database:** SQLite (via `sqlite3`/SQLAlchemy)  
- **Visualization:** matplotlib, seaborn, plotly, Power BI  
- **Utilities:** tqdm, python-dotenv, logging  
- **Version Control:** Git

`requirements.txt` (general list, no pinned versions):
```text
selenium
pandas
numpy
sqlalchemy
python-dotenv
tqdm
matplotlib
seaborn
plotly
requests
beautifulsoup4
jupyter
```

---

## Project Structure
```
mini_project-2/
├─ data/
│  ├─ raw_json/              # Downloaded match JSON files
│  ├─ processed/             # Cleaned/flattened CSV or parquet
│  └─ sqlite/cricket.db      # SQLite database file
├─ notebooks/
│  └─ eda.ipynb              # 10 visualization notebook
├─ src/
│  ├─ scraping/
│  │  └─ download_matches.py # Selenium automation
│  ├─ processing/
│  │  └─ transform_json.py   # JSON→DataFrame cleaning
│  ├─ database/
│  │  ├─ schema.sql          # Table definitions
│  │  └─ load_data.py        # Insert into SQLite
│  ├─ analytics/
│  │  ├─ sql_queries.sql     # 20 queries
│  │  └─ run_queries.py      # Automate query execution
│  └─ viz/
│     └─ export_for_powerbi.py
├─ dashboards/
│  └─ Cricsheet_Insights.pbix
├─ docs/
│  ├─ EDA_Presentation.pptx
│  └─ Project_Report.pdf
├─ requirements.txt
└─ README.md
```

---

## Prerequisites & Installation
### 1. System Requirements
- Windows 10/11, macOS, or Linux
- Python 3.10+
- Google Chrome/Firefox + latest driver
- Power BI Desktop (Windows)

### 2. Clone & Environment
```bash
git clone <repo-url>
cd mini_project-2
python -m venv .venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Variables (`.env`)
```
CRICSHEET_URL=https://cricsheet.org/matches/
DOWNLOAD_DIR=./data/raw_json
SQLITE_DB=./data/sqlite/cricket.db
```

### 4. SQLite Setup
```bash
python src/database/load_data.py --init-db
```
This creates tables `test_matches`, `odi_matches`, `t20_matches`, `ipl_matches`.

### 5. Power BI
- Install from Microsoft Store or official site.
- Enable preview connectors if required.

---

## Data Source
- **URL:** https://cricsheet.org/matches/  
- **Format:** Each match is a JSON file containing `info`, `innings`, `deliveries`, player stats, etc.  
- **Match Types:** Test, ODI, T20, IPL (subset of T20).  
- **Preprocessing:** Load JSON → normalize nested structures → clean datatypes → map teams/players → insert into SQLite tables.

---

## Methodology / Approach
1. **Selenium Scraping**  
   - Launch browser, navigate to match list, filter by format, download JSON links.  
   - Use XPath/CSS selectors with explicit waits.  
   - Store metadata in a list of dictionaries for easier DataFrame conversion.

2. **Data Transformation (Python/Pandas)**  
   - Parse JSON, flatten innings/deliveries, enforce schema, handle nulls, derive KPIs.  
   - Tag each record with match type and unique IDs.

3. **Database Management (SQLite)**  
   - Create normalized tables for each format plus lookup tables (teams, players, venues).  
   - Use SQLAlchemy ORM or raw `sqlite3` for inserts and migrations.

4. **Analytical SQL Queries (20)**  
   - Optimize with indexes (`match_id`, `player_id`, `team_id`).  
   - Categorize into batting, bowling, team, match outcomes.

5. **EDA with Python**  
   - Build at least 10 visualizations (matplotlib, seaborn, plotly).  
   - Save figures + embed in presentation deck.

6. **Power BI Dashboard**  
   - Connect to SQLite via built-in connector.  
   - Create interactive pages: player trends, match outcomes, win/loss analysis, comparative stats.  
   - Publish `.pbix` alongside data snapshot.

---

## Usage Instructions
1. **Scrape JSON Files**
   ```bash
   python src/scraping/download_matches.py --formats test odi t20 ipl --limit 500
   ```
2. **Transform JSON to DataFrames**
   ```bash
   python src/processing/transform_json.py --input ./data/raw_json --output ./data/processed
   ```
3. **Load Data into SQLite**
   ```bash
   python src/database/load_data.py --source ./data/processed --db ./data/sqlite/cricket.db
   ```
4. **Execute SQL Queries**
   ```bash
   python src/analytics/run_queries.py --queries src/analytics/sql_queries.sql --db ./data/sqlite/cricket.db
   ```
5. **Run EDA Notebook**
   ```bash
   jupyter notebook notebooks/eda.ipynb
   ```
6. **Open Power BI Dashboard**
   - Launch Power BI Desktop → Open `dashboards/Cricsheet_Insights.pbix`.  
   - Refresh data source if database path changes.

---

## Database Schema (SQLite)
- **Tables:**  
  - `test_matches(match_id, date, venue, team1, team2, winner, margin, ... )`  
  - `odi_matches(...)`  
  - `t20_matches(...)`  
  - `ipl_matches(...)`  
  - Lookup tables: `players`, `teams`, `innings`, `deliveries`.
- **Indexes:** `idx_match_id`, `idx_player_runs`, `idx_team_format`.
- **Relationships:** `deliveries.match_id → matches.match_id`, `deliveries.batter_id → players.player_id`.
- **DB Location:** `data/sqlite/cricket.db`.

Example schema snippet:
```sql
CREATE TABLE test_matches (
    match_id TEXT PRIMARY KEY,
    match_date DATE,
    venue TEXT,
    team1 TEXT,
    team2 TEXT,
    winner TEXT,
    result_margin TEXT,
    toss_winner TEXT,
    toss_decision TEXT,
    player_of_match TEXT
);
```

---

## SQL Queries Documentation
1. Top 10 ODI batsmen by total runs.  
2. Leading wicket-takers in T20 matches.  
3. Team with highest win % in Tests.  
4. Total centuries across all formats.  
5. Matches with narrowest victory margin.  
6. Average run rate by team per format.  
7. Players with most sixes in IPL.  
8. Bowlers with best economy (min overs).  
9. Toss-winning impact on match result.  
10. Highest partnerships per format.  
11. Most Player-of-the-Match awards.  
12. Win/loss record per venue.  
13. Decade-wise performance trends.  
14. Matches ending in draws/ties.  
15. Super-over occurrences in T20/IPL.  
16. Fastest hundreds (balls faced).  
17. Best chase totals per team.  
18. Boundary percentage analysis.  
19. Dismissal type distribution.  
20. Average wickets lost in powerplays.

All queries are stored in `src/analytics/sql_queries.sql` with comments and expected result descriptions.

---

## EDA Visualizations
Create at least 10 plots (matplotlib/seaborn/plotly):
- Runs distribution per format (histogram).  
- Strike rate vs average (scatter).  
- Top wicket-takers bar chart.  
- Team win % heatmap.  
- Toss decision vs match outcome stacked bar.  
- Over-by-over run rate line chart.  
- IPL season points trend (line).  
- Player comparison radar chart (plotly).  
- Venue performance treemap.  
- Match margin box plots.

Save figures to `docs/eda_figures/` and embed in `docs/EDA_Presentation.pptx`.

---

## Power BI Dashboard
- **Data Source:** SQLite database (DirectQuery or Import).  
- **Pages:** Overview, Player Insights, Team Comparisons, Match Outcomes, Advanced Filters.  
- **Features:** Slicers by format/team, drill-through to player cards, tooltips with KPIs, bookmarks for storytelling.  
- **Refresh:** Update dataset after running Python pipeline.  
- **Deliverable:** `dashboards/Cricsheet_Insights.pbix`.

---

## Results & Insights
- Automated download and ingestion of Cricsheet data.  
- Clean, query-ready SQLite schema for all match types.  
- Verified SQL query outputs highlighting top performers and trends.  
- Visual insights: batting momentum, bowling efficiency, toss influence, venue impact.  
- Power BI dashboard for analysts, management, and fans.

---

