-- =====================================================
-- Cricsheet Match Data Analysis - 20 SQL Queries
-- =====================================================

-- Query 1: Top 10 batsmen by total runs in ODI matches
-- Description: Find the top 10 run-scorers in ODI cricket
SELECT 
    player,
    SUM(runs) as total_runs,
    COUNT(DISTINCT match_id) as matches_played,
    AVG(runs) as avg_runs_per_match,
    MAX(runs) as highest_score
FROM odi_batting
GROUP BY player
ORDER BY total_runs DESC
LIMIT 10;

-- Query 2: Leading wicket-takers in T20 matches
-- Description: Find the top 10 wicket-takers in T20 cricket
SELECT 
    player,
    SUM(wickets) as total_wickets,
    COUNT(DISTINCT match_id) as matches_played,
    AVG(wickets) as avg_wickets_per_match,
    SUM(runs_conceded) as total_runs_conceded,
    ROUND(AVG(economy), 2) as avg_economy
FROM t20_bowling
GROUP BY player
HAVING total_wickets > 0
ORDER BY total_wickets DESC
LIMIT 10;

-- Query 3: Team with the highest win percentage in Test cricket
-- Description: Calculate win percentage for each team in Test matches
SELECT 
    team,
    COUNT(*) as total_matches,
    SUM(CASE WHEN winner = team THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN winner != team AND winner IS NOT NULL AND winner != '' THEN 1 ELSE 0 END) as losses,
    SUM(CASE WHEN winner IS NULL OR winner = '' THEN 1 ELSE 0 END) as draws,
    ROUND(CAST(SUM(CASE WHEN winner = team THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 2) as win_percentage
FROM (
    SELECT team1 as team, winner FROM test_matches
    UNION ALL
    SELECT team2 as team, winner FROM test_matches
) as all_teams
GROUP BY team
HAVING total_matches >= 10
ORDER BY win_percentage DESC
LIMIT 10;

-- Query 4: Total number of centuries across all match types
-- Description: Count centuries (100+ runs) scored by players
SELECT 
    'Test' as match_type,
    COUNT(*) as centuries
FROM test_batting
WHERE runs >= 100
UNION ALL
SELECT 
    'ODI' as match_type,
    COUNT(*) as centuries
FROM odi_batting
WHERE runs >= 100
UNION ALL
SELECT 
    'T20' as match_type,
    COUNT(*) as centuries
FROM t20_batting
WHERE runs >= 100
UNION ALL
SELECT 
    'IPL' as match_type,
    COUNT(*) as centuries
FROM ipl_batting
WHERE runs >= 100;

-- Query 5: Matches with the narrowest margin of victory (by runs)
-- Description: Find matches won by the smallest run margin
SELECT 
    match_id,
    date,
    team1,
    team2,
    winner,
    venue
FROM (
    SELECT 
        m.match_id,
        m.date,
        m.team1,
        m.team2,
        m.winner,
        m.venue,
        ABS(SUM(CASE WHEN d.team = m.team1 THEN d.runs_total ELSE 0 END) - 
            SUM(CASE WHEN d.team = m.team2 THEN d.runs_total ELSE 0 END)) as run_margin
    FROM odi_matches m
    JOIN odi_deliveries d ON m.match_id = d.match_id
    WHERE m.winner IS NOT NULL AND m.winner != '' AND m.result = ''
    GROUP BY m.match_id, m.date, m.team1, m.team2, m.winner, m.venue
    HAVING run_margin > 0
    ORDER BY run_margin ASC
    LIMIT 10
);

-- Query 6: Player performance comparison across formats
-- Description: Compare a player's batting average across different formats
SELECT 
    player,
    'Test' as format,
    COUNT(DISTINCT match_id) as matches,
    SUM(runs) as total_runs,
    ROUND(AVG(runs), 2) as avg_runs
FROM test_batting
WHERE player = 'V Kohli'  -- Example player, replace with any player name
GROUP BY player
UNION ALL
SELECT 
    player,
    'ODI' as format,
    COUNT(DISTINCT match_id) as matches,
    SUM(runs) as total_runs,
    ROUND(AVG(runs), 2) as avg_runs
FROM odi_batting
WHERE player = 'V Kohli'
GROUP BY player
UNION ALL
SELECT 
    player,
    'T20' as format,
    COUNT(DISTINCT match_id) as matches,
    SUM(runs) as total_runs,
    ROUND(AVG(runs), 2) as avg_runs
FROM t20_batting
WHERE player = 'V Kohli'
GROUP BY player;

-- Query 7: Team head-to-head statistics
-- Description: Head-to-head record between two specific teams
SELECT 
    team1,
    team2,
    COUNT(*) as total_matches,
    SUM(CASE WHEN winner = team1 THEN 1 ELSE 0 END) as team1_wins,
    SUM(CASE WHEN winner = team2 THEN 1 ELSE 0 END) as team2_wins,
    SUM(CASE WHEN winner IS NULL OR winner = '' THEN 1 ELSE 0 END) as draws
FROM test_matches
WHERE (team1 = 'India' AND team2 = 'Australia') 
   OR (team1 = 'Australia' AND team2 = 'India')
GROUP BY team1, team2;

-- Query 8: Venue-wise performance analysis
-- Description: Analyze team performance at different venues
SELECT 
    venue,
    COUNT(*) as total_matches,
    COUNT(DISTINCT team1) + COUNT(DISTINCT team2) as unique_teams,
    SUM(CASE WHEN winner IS NOT NULL AND winner != '' THEN 1 ELSE 0 END) as completed_matches
FROM odi_matches
WHERE venue IS NOT NULL AND venue != ''
GROUP BY venue
HAVING total_matches >= 5
ORDER BY total_matches DESC
LIMIT 20;

-- Query 9: Year-wise trend analysis of matches
-- Description: Number of matches played each year
SELECT 
    SUBSTR(date, 1, 4) as year,
    COUNT(*) as total_matches,
    COUNT(DISTINCT team1) + COUNT(DISTINCT team2) as unique_teams
FROM odi_matches
WHERE date IS NOT NULL
GROUP BY SUBSTR(date, 1, 4)
ORDER BY year DESC;

-- Query 10: Players with best strike rates in T20 matches (minimum 500 runs)
-- Description: Find players with highest strike rates in T20
SELECT 
    player,
    SUM(runs) as total_runs,
    SUM(balls_faced) as total_balls,
    ROUND(CAST(SUM(runs) AS FLOAT) / SUM(balls_faced) * 100, 2) as strike_rate,
    COUNT(DISTINCT match_id) as matches
FROM t20_batting
GROUP BY player
HAVING SUM(runs) >= 500
ORDER BY strike_rate DESC
LIMIT 10;

-- Query 11: Most economical bowlers in IPL (minimum 20 overs)
-- Description: Find bowlers with best economy rates in IPL
SELECT 
    player,
    SUM(overs) as total_overs,
    SUM(runs_conceded) as total_runs_conceded,
    SUM(wickets) as total_wickets,
    ROUND(AVG(economy), 2) as avg_economy,
    COUNT(DISTINCT match_id) as matches
FROM ipl_bowling
GROUP BY player
HAVING SUM(overs) >= 20
ORDER BY avg_economy ASC
LIMIT 10;

-- Query 12: Players who scored 50+ runs in most matches
-- Description: Find players with most half-centuries (50+ runs)
SELECT 
    player,
    COUNT(*) as half_centuries,
    SUM(runs) as total_runs,
    MAX(runs) as highest_score
FROM (
    SELECT player, runs, match_id FROM test_batting WHERE runs >= 50
    UNION ALL
    SELECT player, runs, match_id FROM odi_batting WHERE runs >= 50
    UNION ALL
    SELECT player, runs, match_id FROM t20_batting WHERE runs >= 50
    UNION ALL
    SELECT player, runs, match_id FROM ipl_batting WHERE runs >= 50
)
GROUP BY player
ORDER BY half_centuries DESC
LIMIT 10;

-- Query 13: Teams with most wins in home conditions
-- Description: Analyze home advantage (assuming venue contains team name or city)
SELECT 
    winner as team,
    COUNT(*) as wins,
    venue
FROM odi_matches
WHERE winner IS NOT NULL 
  AND winner != ''
  AND venue IS NOT NULL
GROUP BY winner, venue
HAVING wins >= 5
ORDER BY wins DESC
LIMIT 15;

-- Query 14: Matches won by teams batting first vs chasing
-- Description: Analyze toss decision impact on match outcome
SELECT 
    toss_decision,
    COUNT(*) as total_matches,
    SUM(CASE WHEN winner = toss_winner THEN 1 ELSE 0 END) as wins_by_toss_winner,
    ROUND(CAST(SUM(CASE WHEN winner = toss_winner THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 2) as win_percentage
FROM odi_matches
WHERE toss_decision IS NOT NULL 
  AND toss_decision != ''
  AND winner IS NOT NULL
  AND winner != ''
GROUP BY toss_decision;

-- Query 15: Players with most player of the match awards
-- Description: Find players who won most player of the match awards
SELECT 
    player_of_match as player,
    COUNT(*) as awards,
    match_type
FROM (
    SELECT player_of_match, 'Test' as match_type FROM test_matches WHERE player_of_match IS NOT NULL AND player_of_match != ''
    UNION ALL
    SELECT player_of_match, 'ODI' as match_type FROM odi_matches WHERE player_of_match IS NOT NULL AND player_of_match != ''
    UNION ALL
    SELECT player_of_match, 'T20' as match_type FROM t20_matches WHERE player_of_match IS NOT NULL AND player_of_match != ''
    UNION ALL
    SELECT player_of_match, 'IPL' as match_type FROM ipl_matches WHERE player_of_match IS NOT NULL AND player_of_match != ''
)
WHERE player_of_match IS NOT NULL AND player_of_match != ''
GROUP BY player_of_match, match_type
ORDER BY awards DESC
LIMIT 20;

-- Query 16: Average runs per over by team in powerplay (first 6 overs)
-- Description: Analyze powerplay performance
SELECT 
    d.team,
    COUNT(DISTINCT d.match_id) as matches,
    SUM(d.runs_total) as total_runs,
    COUNT(*) as total_balls,
    ROUND(CAST(SUM(d.runs_total) AS FLOAT) / COUNT(DISTINCT d.match_id) / 6, 2) as avg_runs_per_over
FROM odi_deliveries d
JOIN odi_matches m ON d.match_id = m.match_id
WHERE d.over <= 6
GROUP BY d.team
HAVING matches >= 10
ORDER BY avg_runs_per_over DESC
LIMIT 10;

-- Query 17: Bowlers with best bowling figures (most wickets in a match)
-- Description: Find best individual bowling performances
SELECT 
    player,
    match_id,
    wickets,
    runs_conceded,
    overs,
    economy
FROM (
    SELECT player, match_id, wickets, runs_conceded, overs, economy FROM test_bowling
    UNION ALL
    SELECT player, match_id, wickets, runs_conceded, overs, economy FROM odi_bowling
    UNION ALL
    SELECT player, match_id, wickets, runs_conceded, overs, economy FROM t20_bowling
    UNION ALL
    SELECT player, match_id, wickets, runs_conceded, overs, economy FROM ipl_bowling
)
ORDER BY wickets DESC, runs_conceded ASC
LIMIT 20;

-- Query 18: Teams with highest average team score
-- Description: Calculate average team scores per match
SELECT 
    team,
    COUNT(DISTINCT match_id) as matches,
    SUM(runs_total) as total_runs,
    ROUND(CAST(SUM(runs_total) AS FLOAT) / COUNT(DISTINCT match_id), 2) as avg_team_score
FROM (
    SELECT team, match_id, SUM(runs_total) as runs_total
    FROM odi_deliveries
    GROUP BY team, match_id
)
GROUP BY team
HAVING matches >= 20
ORDER BY avg_team_score DESC
LIMIT 10;

-- Query 19: Most successful bowling partnerships (wickets taken together)
-- Description: Analyze bowling partnerships (same match, different bowlers)
-- Note: This is a simplified version - actual partnerships require more complex logic
SELECT 
    match_id,
    COUNT(DISTINCT player) as bowlers_used,
    SUM(wickets) as total_wickets,
    SUM(runs_conceded) as total_runs
FROM odi_bowling
GROUP BY match_id
HAVING total_wickets >= 8
ORDER BY total_wickets DESC, total_runs ASC
LIMIT 10;

-- Query 20: Overall statistics summary across all formats
-- Description: Comprehensive summary of all match types
SELECT 
    'Test' as format,
    COUNT(DISTINCT match_id) as total_matches,
    COUNT(DISTINCT player) as unique_players,
    SUM(runs) as total_runs_scored
FROM test_batting
UNION ALL
SELECT 
    'ODI' as format,
    COUNT(DISTINCT match_id) as total_matches,
    COUNT(DISTINCT player) as unique_players,
    SUM(runs) as total_runs_scored
FROM odi_batting
UNION ALL
SELECT 
    'T20' as format,
    COUNT(DISTINCT match_id) as total_matches,
    COUNT(DISTINCT player) as unique_players,
    SUM(runs) as total_runs_scored
FROM t20_batting
UNION ALL
SELECT 
    'IPL' as format,
    COUNT(DISTINCT match_id) as total_matches,
    COUNT(DISTINCT player) as unique_players,
    SUM(runs) as total_runs_scored
FROM ipl_batting;

