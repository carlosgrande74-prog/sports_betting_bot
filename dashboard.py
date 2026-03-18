import sys

# --- PYTHON 3.14 KOMPATIBILITÁSI JAVÍTÁS ---
# Ez a rész becsapja a rendszert, ha hiányzik az imghdr modul
try:
    import imghdr
except ImportError:
    try:
        import pure_python_imghdr as imghdr
        sys.modules['imghdr'] = imghdr
    except ImportError:
        # Ha még a pótlék sincs fent, létrehozunk egy üres objektumot, hogy ne omoljon össze
        from types import ModuleType
        fake_imghdr = ModuleType('imghdr')
        fake_imghdr.what = lambda x, h=None: None
        sys.modules['imghdr'] = fake_imghdr
# -------------------------------------------

import streamlit as st
import pandas as pd
import os
from calculator import FootballPredictor

# Oldal konfigurációja
st.set_page_config(page_title="Profi Foci Bot", page_icon="⚽", layout="wide")

# Stílus beállítása (Sötét téma, zöld színekkel)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { background-color: #26a69a; color: white; width: 100%; border-radius: 5px; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_stdio=True)

def main():
    st.title("⚽ Profi Foci Prediktor v1.0")
    st.write("Add meg az oddsokat az elemzéshez!")

    # Oldalsáv az adatoknak
    st.sidebar.header("Meccs Adatok")
    h_odds = st.sidebar.number_input("Hazai Odds (H)", min_value=1.01, value=2.10, step=0.01)
    d_odds = st.sidebar.number_input("Döntetlen Odds (D)", min_value=1.01, value=3.20, step=0.01)
    v_odds = st.sidebar.number_input("Vendég Odds (V)", min_value=1.01, value=3.50, step=0.01)

    # Számítás gomb
    if st.sidebar.button("Elemzés Futtatása"):
        predictor = FootballPredictor()
        
        # Elméleti valószínűségek kiszámítása (egyszerűsített modell)
        prob_h, prob_d, prob_v = predictor.calculate_probabilities(h_odds, d_odds, v_odds)
        
        # Eredmények megjelenítése
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Hazai Esély", f"{prob_h:.1%}")
        with col2:
            st.metric("Döntetlen Esély", f"{prob_d:.1%}")
        with col3:
            st.metric("Vendég Esély", f"{prob_v:.1%}")

        st.divider()

        # Ajánlás rész
        st.subheader("🤖 AI Ajánlata")
        
        # Logika az ajánláshoz
        if prob_h > 0.55:
            st.success("ERŐS TIPP: Hazai Győzelem (H)")
        elif prob_v > 0.45:
            st.warning("VENDÉG ESÉLY: Érdemes megfontolni a V-t")
        elif prob_d > 0.35:
            st.info("SZOROS MECCS: A Döntetlen esélye magasabb az átlagnál")
        else:
            st.write("Nincs elég nagy különbség a biztonságos tipphez.")

    else:
        st.info("Változtasd meg az oddsokat a bal oldalon, majd nyomj az 'Elemzés Futtatása' gombra!")

if __name__ == "__main__":
    main()