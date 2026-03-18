import pandas as pd
from scipy.stats import poisson

def calculate_team_strengths(df):
    """Kiszámolja a csapatok támadó és védekező erejét a történelmi adatokból."""
    df = df.dropna(subset=['FTHG', 'FTAG']).copy()
    
    league_home_avg = df['FTHG'].mean()
    league_away_avg = df['FTAG'].mean()
    
    home_stats = df.groupby('HomeTeam').agg({'FTHG': 'mean', 'FTAG': 'mean'}).reset_index()
    home_stats.columns = ['Team', 'HomeGoalsScored', 'HomeGoalsConceded']
    home_stats['HomeAttack'] = home_stats['HomeGoalsScored'] / league_home_avg
    home_stats['HomeDefense'] = home_stats['HomeGoalsConceded'] / league_away_avg
    
    away_stats = df.groupby('AwayTeam').agg({'FTAG': 'mean', 'FTHG': 'mean'}).reset_index()
    away_stats.columns = ['Team', 'AwayGoalsScored', 'AwayGoalsConceded']
    away_stats['AwayAttack'] = away_stats['AwayGoalsScored'] / league_away_avg
    away_stats['AwayDefense'] = away_stats['AwayGoalsConceded'] / league_home_avg
    
    strengths = pd.merge(home_stats, away_stats, on='Team')
    return strengths, league_home_avg, league_away_avg

def predict_match(home_team, away_team, strengths, league_home_avg, league_away_avg):
    """Kiszámolja a meccs kimenetelének valószínűségeit."""
    try:
        home_data = strengths[strengths['Team'] == home_team].iloc[0]
        away_data = strengths[strengths['Team'] == away_team].iloc[0]
    except IndexError:
        return "Hiba: Az egyik csapat nem található az adatbázisban."
        
    home_xg = home_data['HomeAttack'] * away_data['AwayDefense'] * league_home_avg
    away_xg = away_data['AwayAttack'] * home_data['HomeDefense'] * league_away_avg
    
    home_win_prob, draw_prob, away_win_prob = 0, 0, 0
    
    for home_goals in range(6):
        for away_goals in range(6):
            prob = poisson.pmf(home_goals, home_xg) * poisson.pmf(away_goals, away_xg)
            if home_goals > away_goals:
                home_win_prob += prob
            elif home_goals == away_goals:
                draw_prob += prob
            else:
                away_win_prob += prob
                
    return {
        'Hazai xG': round(home_xg, 2),
        'Vendég xG': round(away_xg, 2),
        'Hazai Esély (%)': round(home_win_prob * 100, 2),
        'Döntetlen Esély (%)': round(draw_prob * 100, 2),
        'Vendég Esély (%)': round(away_win_prob * 100, 2)
    }

def calculate_kelly_criterion(probability, odds, multiplier=0.5):
    """
    Kiszámolja az ajánlott tétet a Kelly-kritérium alapján.
    A multiplier (szorzó) segít csökkenteni a kockázatot (pl. Fél-Kelly = 0.5).
    """
    if probability <= 0 or odds <= 1.0:
        return 0.0
        
    # Kelly formula: f = (p * O - 1) / (O - 1)
    f = (probability * odds - 1) / (odds - 1)
    
    if f <= 0:
        return 0.0 # Nincs érték
        
    return f * multiplier