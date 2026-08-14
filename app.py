import streamlit as st
import math

st.set_page_config(page_title="Ski Way Diving Machine", page_icon="🤿", layout="centered")

st.title("🤿 Ski Way Diving Machine")
st.subheader("Automatyczny planer profili, rezerw i limitów czasowych")
st.write("---")

tab1, tab2 = st.tabs(["📋 Planowanie Nurkowania", "🔬 Zaawansowane Parametry"])

with tab1:
    st.markdown("### Krok 1: Twój Sprzęt i Gaz")
    col1, col2 = st.columns(2)
    with col1:
        opcje_butli = {"7 L": 7, "10 L": 10, "12 L": 12, "15 L": 15, "18 L": 18, "2x10 L": 20, "2x12 L": 24}
        wybrana_butla_tekst = st.selectbox("Pojemność butli:", list(opcje_butli.keys()), index=3)
        pojemnosc_butli = opcje_butli[wybrana_butla_tekst]
    with col2:
        typ_gazu = st.radio("Rodzaj gazu:", ["Powietrze", "Nitrox"], horizontal=True)

    fo2 = st.slider("Zawartość tlenu (% O₂):", 21, 40, 32) / 100 if typ_gazu == "Nitrox" else 0.21

    st.write("---")
    st.markdown("### Krok 2: Profil Planowanego Nurkowania")
    col_prof1, col_prof2 = st.columns(2)
    with col_prof1: glebokosc = st.number_input("Planowana głębokość (metry):", 1, 50, 30, step=1)
    with col_prof2: czas_na_dnie = st.number_input("Twój planowany czas na dnie (minuty):", 1, 90, 15, step=1)

    if glebokosc <= 10: lim_ndl = 120
    elif glebokosc <= 30: lim_ndl = 20
    else: lim_ndl = 5

    czas_deco = math.ceil((czas_na_dnie - lim_ndl) * 1.5) if czas_na_dnie > lim_ndl else 0
    cisnienie_startowe = 200
    gestosc_na_dnie = 1.29 * ((glebokosc / 10) + 1)

with tab2:
    st.markdown("### Dostosuj parametry fizjologiczne")
    sac_indywidualne = st.slider("Twoje standardowe zużycie (SAC) [l/min]:", 10, 30, 20)
    ppo2_custom = st.slider("Limit ciśnienia parcjalnego tlenu (PPO₂):", 1.2, 1.6, 1.4, 0.1)
    mod_metry = (ppo2_custom / fo2 - 1) * 10

# --- AUTOMATYCZNY SILNIK OBLICZENIOWY ---
sac_awaryjne = sac_indywidualne * 2
p_dno = (glebokosc / 10) + 1
p_przystanek = (6 / 10) + 1
p_powierzchnia = 1.0

gaz_faza_stres = 2 * sac_awaryjne * p_dno
gaz_faza_wynurzanie_glebokie = (((glebokosc - 6) / 9) * sac_awaryjne * ((p_dno + p_przystanek) / 2)) if glebokosc > 6 else 0
gaz_faza_przystanek = (3 + czas_deco) * sac_awaryjne * p_przystanek
gaz_faza_wynurzanie_plytkie = 2 * sac_awaryjne * ((p_przystanek + p_powierzchnia) / 2)

calkowity_gaz_litry = gaz_faza_stres + gaz_faza_wynurzanie_glebokie + gaz_faza_przystanek + gaz_faza_wynurzanie_plytkie
rock_bottom_bar = math.ceil((calkowity_gaz_litry / pojemnosc_butli) / 10) * 10
dostepny_gaz_bar = cisnienie_startowe - rock_bottom_bar

zuzycie_denne_bar_min = (sac_indywidualne * p_dno) / pojemnosc_butli
maks_czas_na_dnie = math.floor(dostepny_gaz_bar / zuzycie_denne_bar_min) if dostepny_gaz_bar > 0 else 0
planowane_zuzycie_bar = math.ceil(czas_na_dnie * zuzycie_denne_bar_min)
turn_pressure_bar = max(rock_bottom_bar, cisnienie_startowe - planowane_zuzycie_bar)

st.write("---")
st.markdown("### 📊 Raport Bezpieczeństwa Profilu:")
res_col1, res_col2 = st.columns(2)
res_col1.metric("🚨 BEZWZGLĘDNY ROCK BOTTOM", f"{rock_bottom_bar} BAR")
res_col2.metric("⏱️ MAKSYMALNY CZAS NA DNIE", f"{maks_czas_na_dnie} MIN")
