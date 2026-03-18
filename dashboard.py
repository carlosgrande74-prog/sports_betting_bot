import streamlit as st
import pandas as pd
import calculator as calc
import os

st.set_page_config(page_title="Profi Fogadási Rendszer", layout="wide")

# --- NÉVEGYESÍTŐ SZÓTÁR ---
# Az élő oddsok és a statisztikák néha eltérően írják a csapatokat
TEAM_MAPPING = {
    "Manchester United": "Man United",
    "Manchester City": "Man City",
    "Newcastle United": "Newcastle",
    "Tottenham Hotspur": "Tottenham",
    "Nottingham Forest": "Nott'm Forest",
    "Wolverhampton Wanderers": "Wolves",
    "Brighton and Hove Albion": "Brighton",
    "West Ham United": "West Ham",
    "Leicester City": "Leicester",
    "Ipswich Town": "Ipswich",
    "Everton FC": "Everton"
}

def normalize_name(name):
    return TEAM_MAPPING.get(name, name)

# --- OLDALSÁV (SIDEBAR) ---
st.sidebar.header("💰 Bankroll Menedzsment")
bankroll = st.sidebar.number_input("Teljes Tőke (Ft)", min_value=1000, value=100000, step=5000)
kelly_options = {"Óvatos (Negyed-Kelly)": 0.25, "Normál (Fél-Kelly)": 0.50, "Agresszív (Teljes-Kelly)": 1.0}
kelly_choice = st.sidebar.selectbox("Kockázati szint", list(kelly_options.keys()), index=1)
kelly_mult = kelly_options[kelly_choice]

st.title("⚽ Profi Fogadási Rendszer")

@st.cache_data
def load_data():
    hist_df = pd.read_csv("data/premier_league_historical.csv")
    live_df = None
    if os.path.exists("data/live_odds.csv"):
        live_df = pd.read_csv("data/live_odds.csv")
    return hist_df, live_df

try:
    hist_df, live_df = load_data()
    strengths, h_avg, a_avg = calc.calculate_team_strengths(hist_df)
    
    # --- AUTOMATIKUS ROBOT SZEKCIÓ ---
    st.header("🤖 Automatikus Hétvégi Értékkereső")
    
    if live_df is not None and not live_df.empty:
        st.write("A robot automatikusan átvizsgálta a letöltött hétvégi meccseket, összehasonlította az élő szorzókat a matematikai modellel, és ezeket a +EV fogadásokat találta:")
        
        found_value = False
        
        for index, row in live_df.iterrows():
            home_api = row['Hazai']
            away_api = row['Vendég']
            
            # Nevek egységesítése
            home = normalize_name(home_api)
            away = normalize_name(away_api)
            
            result = calc.predict_match(home, away, strengths, h_avg, a_avg)
            
            # Ha hiba volt (pl. új feljutó csapat, aki még nincs az adatbázisban), ugorjuk át
            if isinstance(result, str): 
                continue
                
            # Hazai Value keresése
            ev_home = (result['Hazai Esély (%)'] / 100 * row['Hazai Odds']) - 1
            if ev_home > 0:
                rec_pct = calc.calculate_kelly_criterion(result['Hazai Esély (%)'] / 100, row['Hazai Odds'], kelly_mult)
                rec_huf = int(bankroll * rec_pct)
                if rec_huf > 0:
                    found_value = True
                    st.success(f"🔥 **{home} győzelem** ({home} vs {away}) | Iroda: {row['Iroda']} | Szorzó: **{row['Hazai Odds']}** | Előny: +{ev_home*100:.1f}% | **Ajánlott Tét: {rec_huf} Ft**")
                    
            # Döntetlen Value keresése
            ev_draw = (result['Döntetlen Esély (%)'] / 100 * row['Döntetlen Odds']) - 1
            if ev_draw > 0:
                rec_pct = calc.calculate_kelly_criterion(result['Döntetlen Esély (%)'] / 100, row['Döntetlen Odds'], kelly_mult)
                rec_huf = int(bankroll * rec_pct)
                if rec_huf > 0:
                    found_value = True
                    st.info(f"⚖️ **Döntetlen** ({home} vs {away}) | Iroda: {row['Iroda']} | Szorzó: **{row['Döntetlen Odds']}** | Előny: +{ev_draw*100:.1f}% | **Ajánlott Tét: {rec_huf} Ft**")
                    
            # Vendég Value keresése
            ev_away = (result['Vendég Esély (%)'] / 100 * row['Vendég Odds']) - 1
            if ev_away > 0:
                rec_pct = calc.calculate_kelly_criterion(result['Vendég Esély (%)'] / 100, row['Vendég Odds'], kelly_mult)
                rec_huf = int(bankroll * rec_pct)
                if rec_huf > 0:
                    found_value = True
                    st.success(f"🔥 **{away} győzelem** ({home} vs {away}) | Iroda: {row['Iroda']} | Szorzó: **{row['Vendég Odds']}** | Előny: +{ev_away*100:.1f}% | **Ajánlott Tét: {rec_huf} Ft**")
                    
        if not found_value:
            st.warning("Jelenleg a rendszer egyetlen közelgő meccsben sem talált matematikai értéket (+EV). Az irodák jól lőtték be a szorzókat! Várj 1-2 napot és frissítsd az oddsokat!")
            
    else:
        st.info("Még nincsenek letöltve az élő szorzók. Futtasd a 'get_live_odds.py' scriptet!")
        
    st.write("---")
    
    # --- KÉZI KALKULÁTOR SZEKCIÓ (Elrejtve, kinyitható) ---
    with st.expander("🛠️ Kézi Kalkulátor Megnyitása (Ha te magad akarsz oddsot ellenőrizni)"):
        teams = sorted(strengths['Team'].tolist())
        col1, col2 = st.columns(2)
        with col1:
            home_team = st.selectbox("Hazai Csapat", teams, index=teams.index("Arsenal") if "Arsenal" in teams else 0)
        with col2:
            away_team = st.selectbox("Vendég Csapat", teams, index=teams.index("Chelsea") if "Chelsea" in teams else 1)
            
        if home_team != away_team:
            result = calc.predict_match(home_team, away_team, strengths, h_avg, a_avg)
            real_home_odds = 100 / result['Hazai Esély (%)'] if result['Hazai Esély (%)'] > 0 else 0
            real_draw_odds = 100 / result['Döntetlen Esély (%)'] if result['Döntetlen Esély (%)'] > 0 else 0
            real_away_odds = 100 / result['Vendég Esély (%)'] if result['Vendég Esély (%)'] > 0 else 0
            
            res_col1, res_col2, res_col3 = st.columns(3)
            res_col1.metric(f"{home_team}", f"{real_home_odds:.2f}", f"Esély: {result['Hazai Esély (%)']}%", "off")
            res_col2.metric("Döntetlen", f"{real_draw_odds:.2f}", f"Esély: {result['Döntetlen Esély (%)']}%", "off")
            res_col3.metric(f"{away_team}", f"{real_away_odds:.2f}", f"Esély: {result['Vendég Esély (%)']}%", "off")
            
except FileNotFoundError:
    st.error("Nem található a történelmi adatfájl. Kérlek, futtasd le a get_historical_data.py scriptet!")