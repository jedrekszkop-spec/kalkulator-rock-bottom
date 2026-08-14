import streamlit as st
import math

st.set_page_config(page_title="DeepPlan – Asystent Nurkowy", page_icon="🤿", layout="centered")

st.title("🤿 DeepPlan")
st.subheader("Twój osobisty asystent planowania i bezpieczeństwa")
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

    if typ_gazu == "Nitrox":
        nitrox_procent = st.slider("Zawartość tlenu (% O₂):", 21, 40, 32)
        fo2 = nitrox_procent / 100
    else:
        fo2 = 0.21

    st.write("---")
    st.markdown("### Krok 2: Profil Nurkowania")
    glebokosc = st.number_input("Planowana głębokość (metry):", min_value=1, max_value=50, value=30, step=1)
    
    ma_deco = st.checkbox("Planuję wejść w dekompresję (Deco Stop)")
    czas_deco = st.number_input("Czas przystanków dekompresyjnych (min):", 1, 60, 5) if ma_deco else 0

    cisnienie_startowe = 200
    ppo2_limit = 1.4
    mod_metry = (ppo2_limit / fo2 - 1) * 10
    
    if glebokosc <= 10: ndl_tekst = "Brak limitu (100+ min)"
    elif glebokosc <= 30: ndl_tekst = "ok. 20 min"
    else: ndl_tekst = "Poniżej 5 min!"

    gestosc_na_dnie = 1.29 * ((glebokosc / 10) + 1)

with tab2:
    st.markdown("### Dostosuj parametry fizjologiczne")
    sac_indywidualne = st.slider("Twoje standardowe zużycie (SAC) [l/min]:", 10, 30, 20)
    ppo2_custom = st.slider("Limit ciśnienia parcjalnego tlenu (PPO₂):", 1.2, 1.6, 1.4, 0.1)
    mod_metry = (ppo2_custom / fo2 - 1) * 10

# --- SILNIK OBLICZENIOWY ---
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

st.write("---")
st.markdown("### 📊 Raport Bezpieczeństwa:")
res_col1, res_col2 = st.columns(2)
res_col1.metric("🚨 ROCK BOTTOM", f"{rock_bottom_bar} BAR")
res_col2.metric("🟢 GAZ NA FAZĘ DENNĄ", f"{dostepny_gaz_bar} BAR" if dostepny_gaz_bar > 0 else "BRAK")
