import pandas as pd
import os

def download_premier_league_data():
    """
    Letölti az angol Premier League aktuális és előző szezonjának adatait
    a football-data.co.uk oldalról.
    """
    # Létrehozzuk a data mappát a gyökérkönyvtárban, ha még nem létezik
    os.makedirs("data", exist_ok=True)
    
    print("Adatok letöltése folyamatban...")
    
    # 2024/2025-ös és 2025/2026-os szezon linkjei (ha már van)
    urls = [
        "https://www.football-data.co.uk/mmz4281/2425/E0.csv",
        "https://www.football-data.co.uk/mmz4281/2526/E0.csv" 
    ]
    
    dataframes = []
    
    for url in urls:
        try:
            df = pd.read_csv(url)
            dataframes.append(df)
            print(f"Sikeres letöltés: {url}")
        except Exception as e:
            # Ha a jövőbeli szezon még nincs fent, azt is elegánsan kezeli
            print(f"Ezt a fájlt még nem lehet letölteni (lehet, hogy még nem kezdődött el a szezon): {url}")
            
    # Ha van letöltött adatunk, összefűzzük és elmentjük
    if dataframes:
        master_df = pd.concat(dataframes, ignore_index=True)
        save_path = "data/premier_league_historical.csv"
        master_df.to_csv(save_path, index=False)
        print(f"\nKész! {len(master_df)} mérkőzés adata elmentve ide: {save_path}")
    else:
        print("\nNem sikerült adatot letölteni.")

if __name__ == "__main__":
    download_premier_league_data()