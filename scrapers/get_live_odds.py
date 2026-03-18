import requests
import pandas as pd
import os

# IDE MÁSOLD BE A SAJÁT KULCSODAT A MACSKAKÖRMÖK KÖZÉ!
API_KEY = "cdbfe9566b57f491454a1b0c93dd1b4f"
SPORT = "soccer_epl" # Angol Premier League

def get_upcoming_odds():
    print("Élő szorzók lekérdezése a hétvégi meccsekhez...")
    
    # Lekérjük az adatokat európai irodáktól (pl. Unibet, Bet365)
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Hiba a letöltésnél! Ellenőrizted az API kulcsot?")
        return
        
    data = response.json()
    games = []
    
    for event in data:
        home_team = event['home_team']
        away_team = event['away_team']
        start_time = event['commence_time']
        
        # Keresünk egy fogadóirodát az eseményhez
        if not event['bookmakers']:
            continue
            
        bookie = event['bookmakers'][0] # Vesszük az első elérhető európai irodát
        market = bookie['markets'][0]
        
        odds = {}
        for outcome in market['outcomes']:
            odds[outcome['name']] = outcome['price']
            
        games.append({
            'Dátum': start_time[:10],
            'Hazai': home_team,
            'Vendég': away_team,
            'Iroda': bookie['title'],
            'Hazai Odds': odds.get(home_team, 0),
            'Döntetlen Odds': odds.get('Draw', 0),
            'Vendég Odds': odds.get(away_team, 0)
        })
        
    if games:
        os.makedirs("../data", exist_ok=True)
        # Itt figyelünk, hogy jó helyre mentsen (a data mappába)
        save_path = "data/live_odds.csv" if os.path.exists("data") else "../data/live_odds.csv"
        
        df = pd.DataFrame(games)
        df.to_csv(save_path, index=False)
        print(f"\n✅ Kész! {len(df)} közelgő meccs élő szorzói elmentve ide: {save_path}")
    else:
        print("Nincs elérhető közelgő mérkőzés jelenleg.")

if __name__ == "__main__":
    get_upcoming_odds()