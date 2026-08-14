import streamlit as st
import math

# Konfiguracja strony
st.set_page_config(page_title="Zaawansowany Planer Nurkowy", page_icon="🤿", layout="centered")

st.title("🤿 Zaawansowany Agent Planowania Nurkowań")
st.write("Profesjonalne narzędzie do obliczania Rock Bottom, limitów NDL oraz MOD dla dowolnego Nitroxu.")

# --- SEKCJA 1: PARAMETRY NURKA I SPRZĘTU ---
st.header("1. Parametry Nurka i Sprzętu")

col1, col2 = st.columns(2)
with col1:
    opcje_butli = {
        "7 litrów (Stage / Mała)": 7,
        "10 litrów": 10,
        "12 litrów (Standard)": 12,
        "15 litrów (Duża)": 15,
        "18 litrów (Bardzo duża)": 18,
        "2x10 litrów (Twins 20L)": 20,
        "2x12 litrów (Twins 24L)": 24
    }
    wybrana_butla_tekst = st.selectbox("Pojemność Twojej butli (litry):", list(opcje_butli.keys()), index=3)
    pojemnosc_butli = opcje_butli[wybrana_butla_tekst]
    
    typ_gazu = st.radio("Rodzaj używanego gazu:", ["Zwykłe powietrze", "Nitrox (mieszanka wzbogacona)"])

with col2:
    sac_indywidualne = st.slider("Twoje zużycie powierzchniowe (SAC) [l/min]:", min_value=10, max_value=30, value=20, step=1)
    cisnienie_startowe = 200
    
    if typ_gazu == "Nitrox (mieszanka wzbogacona)":
        nitrox_procent = st.slider("Zawartość tlenu (% O₂):", min_value=21, max_value=40, value=32, step=1)
        fo2 = nitrox_procent / 100
    else:
        fo2 = 0.21

# Obliczanie MOD dla PPO2 = 1.4
ppo2_limit = 1.4
mod_metry = (ppo2_limit / fo2 - 1) * 10

if typ_gazu == "Zwykłe powietrze":
    st.info(f"✨ Nurkujesz na **Powietrzu**. Twoja Maksymalna Głębokość Operacyjna (MOD) ze względu na tlen wynosi: **{mod_metry:.1f} m**.")
else:
    st.info(f"✨ Nurkujesz na **Nitroxie {int(fo2*100)}**. Twoja Maksymalna Głębokość Operacyjna (MOD) wynosi: **{mod_metry:.1f} m** (przy $PPO_2$ = 1.4)")

# --- SEKCJA 2: PARAMETRY PROFILU ---
st.header("2. Profil Planowanego Nurkowania")

glebokosc = st.number_input("Planowana głębokość nurkowania (metry):", min_value=1, max_value=50, value=30, step=1)

if glebokosc > mod_metry:
    st.error(f"🚨 NIEBEZPIECZEŃSTWO! Planowana głębokość ({glebokosc}m) przekracza bezpieczną granicę MOD ({mod_metry:.1f}m) dla tej mieszanki! Ryzyko toksyczności tlenowej!")

if glebokosc <= 10: ndl_tekst = "Brak limitu (ponad 100+ min)"
elif glebokosc <= 12: ndl_tekst = "ok. 120 minut"
elif glebokosc <= 15: ndl_tekst = "ok. 75 minut"
elif glebokosc <= 18: ndl_tekst = "ok. 50 minut"
elif glebokosc <= 22: ndl_tekst = "ok. 35 minut"
elif glebokosc <= 25: ndl_tekst = "ok. 25 minut"
elif glebokosc <= 30: ndl_tekst = "ok. 20 minut"
elif glebokosc <= 35: ndl_tekst = "ok. 14 minut"
elif glebokosc <= 40: ndl_tekst = "ok. 9 minut"
else: ndl_tekst = "Poniżej 5 min!"

st.warning(f"⏱️ Szacowany limit bezdekompresyjny (NDL) dla {glebokosc}m wynosi: **{ndl_tekst}**")

# --- SEKCJA 3: ROCK BOTTOM ---
sac_awaryjne = sac_indywidualne * 2
p_dno = (glebokosc / 10) + 1
p_przystanek = (6 / 10) + 1
p_powierzchnia = 1.0

gaz_faza_stres = 2 * sac_awaryjne * p_dno

if glebokosc > 6:
    dystans_faza1 = glebokosc - 6
    czas_faza1 = dystans_faza1 / 9
    p_sr_faza1 = (p_dno + p_przystanek) / 2
    gaz_faza_wynurzanie_glebokie = czas_faza1 * sac_awaryjne * p_sr_faza1
else:
    gaz_faza_wynurzanie_glebokie = 0

gaz_faza_przystanek = 3 * sac_awaryjne * p_przystanek

czas_faza2 = 6 / 3
p_sr_faza2 = (p_przystanek + p_powierzchnia) / 2
gaz_faza_wynurzanie_plytkie = czas_faza2 * sac_awaryjne * p_sr_faza2

calkowity_gaz_litry = gaz_faza_stres + gaz_faza_wynurzanie_glebokie + gaz_faza_przystanek + gaz_faza_wynurzanie_plytkie
rock_bottom_bar = math.ceil((calkowity_gaz_litry / pojemnosc_butli) / 10) * 10
dostepny_gaz_bar = cisnienie_startowe - rock_bottom_bar

st.header("3. Analiza Bezpieczeństwa Gazowego")
st.error(f"🔴 TWÓJ ROCK BOTTOM: {rock_bottom_bar} bar")

if dostepny_gaz_bar > 0:
    st.success(f"🟢 Gaz dostępny na fazę denną: {dostepny_gaz_bar} bar")
else:
    st.error("⚠️ PLAN NIEBEZPIECZNY! Sam powrót awaryjny wymaga więcej gazu niż mieści Twoja butla!")

with st.expander("🔍 Zobacz szczegółowy podział litrów gazu na fazy powrotu:"):
    st.write(f"*   **Stres i rozwiązanie problemu na dnie (2 min):** {round(gaz_faza_stres)} litrów")
    st.write(f"*   **Wynurzenie na głębokość 6 metrów:** {round(gaz_faza_wynurzanie_glebokie)} litrów")
    st.write(f"*   **Przystanek bezpieczeństwa (3 min na 6m):** {round(gaz_faza_przystanek)} litrów")
    st.write(f"*   **Wynurzenie z 6m do powierzchni (2 min):** {round(gaz_faza_wynurzanie_plytkie)} litrów")
