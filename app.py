import streamlit as st
import math

# 1. Konfiguracja aplikacji i nazwy w oknie przeglądarki
st.set_page_config(page_title="Ski Way Diving Machine", page_icon="🤿", layout="centered")

# Nagłówek aplikacji
st.title("🤿 Ski Way Diving Machine")
st.subheader("Automatyczny planer profili, rezerw i limitów czasowych")
st.write("---")

# Podział na zakładki
tab1, tab2 = st.tabs(["📋 Planowanie Nurkowania", "🔬 Zaawansowane Parametry"])

with tab1:
    st.markdown("### Krok 1: Twój Sprzęt i Gaz")
    
    col1, col2 = st.columns(2)
    with col1:
        opcje_butli = {
            "7 L (Stage)": 7,
            "10 L": 10,
            "12 L (Standard)": 12,
            "15 L (Duża)": 15,
            "18 L (Bardzo duża)": 18,
            "2x10 L (Twins)": 20,
            "2x12 L (Twins)": 24
        }
        wybrana_butla_tekst = st.selectbox("Pojemność butli:", list(opcje_butli.keys()), index=3)
        pojemnosc_butli = opcje_butli[wybrana_butla_tekst]
        
    with col2:
        typ_gazu = st.radio("Rodzaj gazu:", ["Powietrze", "Nitrox"], horizontal=True)

    # Dynamiczny suwak dla Nitroxu
    if typ_gazu == "Nitrox":
        nitrox_procent = st.slider("Zawartość tlenu (% O₂):", min_value=21, max_value=40, value=32, step=1)
        fo2 = nitrox_procent / 100
    else:
        fo2 = 0.21

    st.write("---")
    st.markdown("### Krok 2: Profil Planowanego Nurkowania")
    
    col_prof1, col_prof2 = st.columns(2)
    with col_prof1:
        glebokosc = st.number_input("Planowana głębokość (metry):", min_value=1, max_value=50, value=30, step=1)
    with col_prof2:
        # Ten czas służy teraz do sprawdzenia dekompresji
        czas_na_dnie = st.number_input("Twój planowany czas na dnie (minuty):", min_value=1, max_value=90, value=15, step=1)

    # --- BAZA DANYCH NDL ---
    if glebokosc <= 10: lim_ndl = 120
    elif glebokosc <= 12: lim_ndl = 100
    elif glebokosc <= 15: lim_ndl = 75
    elif glebokosc <= 18: lim_ndl = 50
    elif glebokosc <= 22: lim_ndl = 35
    elif glebokosc <= 25: lim_ndl = 25
    elif glebokosc <= 30: lim_ndl = 20
    elif glebokosc <= 35: lim_ndl = 14
    elif glebokosc <= 40: lim_ndl = 9
    else: lim_ndl = 5

    # --- INTELIGENTNE I AUTOMATYCZNE PRZYPISYWANIE CZASU DEKOMPRESJI (Deco Stop) ---
    if czas_na_dnie > lim_ndl:
        minuty_przekroczenia = czas_na_dnie - lim_ndl
        czas_deco = math.ceil(minuty_przekroczenia * 1.5)
        jest_w_deco = True
    else:
        czas_deco = 0
        jest_w_deco = False

    cisnienie_startowe = 200
    gestosc_na_dnie = 1.29 * ((glebokosc / 10) + 1)

with tab2:
    st.markdown("### Dostosuj parametry fizjologiczne")
    sac_indywidualne = st.slider("Twoje standardowe zużycie (SAC) [l/min]:", min_value=10, max_value=30, value=20, step=1)
    ppo2_custom = st.slider("Limit ciśnienia parcjalnego tlenu (PPO₂):", min_value=1.2, max_value=1.6, value=1.4, step=0.1)
    
    mod_metry = (ppo2_custom / fo2 - 1) * 10

# --- SILNIK OBLICZENIOWY ROCK BOTTOM ---
sac_awaryjne = sac_indywidualne * 2
p_dno = (glebokosc / 10) + 1
p_przystanek = (6 / 10) + 1
p_powierzchnia = 1.0

# Obliczanie fazowe litrów awaryjnych
gaz_faza_stres = 2 * sac_awaryjne * p_dno

if glebokosc > 6:
    dystans_faza1 = glebokosc - 6
    czas_faza1 = dystans_faza1 / 9
    p_sr_faza1 = (p_dno + p_przystanek) / 2
    gaz_faza_wynurzanie_glebokie = czas_faza1 * sac_awaryjne * p_sr_faza1
else:
    gaz_faza_wynurzanie_glebokie = 0

calkowity_czas_na_6m = 3 + czas_deco
gaz_faza_przystanek = calkowity_czas_na_6m * sac_awaryjne * p_przystanek

czas_faza2 = 6 / 3
p_sr_faza2 = (p_przystanek + p_powierzchnia) / 2
gaz_faza_wynurzanie_plytkie = time_faza2 = 6 / 3
gaz_faza_wynurzanie_plytkie = czas_faza2 * sac_awaryjne * p_sr_faza2

# Suma rezerwy Rock Bottom
calkowity_gaz_litry = gaz_faza_stres + gaz_faza_wynurzanie_glebokie + gaz_faza_przystanek + gaz_faza_wynurzanie_plytkie
rock_bottom_bar = math.ceil((calkowity_gaz_litry / pojemnosc_butli) / 10) * 10
dostepny_gaz_bar = cisnienie_startowe - rock_bottom_bar

# --- NOWOŚĆ: OBLICZENIA MAKSYMALNEGO CZASU DENNEGO I TURN PRESSURE ---
# Zużycie litrów na minutę na dnie w normalnych warunkach (tylko Ty, bez stresu)
zuzycie_denne_litry_min = sac_indywidualne * p_dno
zuzycie_denne_bar_min = zuzycie_denne_litry_min / pojemnosc_butli

if dostepny_gaz_bar > 0:
    # Maksymalny czas jaki fizycznie nurek może spędzić na dnie do osiągnięcia Rock Bottom
    maks_czas_na_dnie_fizyczny = dostepny_gaz_bar / zuzycie_denne_bar_min
    maks_czas_na_dnie = math.floor(maks_czas_na_dnie_fizyczny)
else:
    maks_czas_na_dnie = 0

# Obliczanie realnego zużycia gazu dla wpisanego przez użytkownika planowanego czasu
planowane_zuzycie_bar = math.ceil(czas_na_dnie * zuzycie_denne_bar_min)
turn_pressure_bar = cisnienie_startowe - planowane_zuzycie_bar

# Jeśli planowany czas przekracza fizyczne możliwości butli, momentem odwrotu staje się po prostu Rock Bottom
if turn_pressure_bar < rock_bottom_bar:
    turn_pressure_bar = rock_bottom_bar


# --- SEKCJA WYNIKÓW I RAPORTU ---
st.write("---")
st.markdown("### 📊 Raport Bezpieczeństwa Profilu:")

# Wizualne karty główne (Zaktualizowane o instrukcje taktyczne!)
res_col1, res_col2 = st.columns(2)
with res_col1:
    st.metric(label="🚨 BEZWZGLĘDNY ROCK BOTTOM", value=f"{rock_bottom_bar} BAR")
with res_col2:
    st.metric(label="⏱️ MAKSYMALNY CZAS NA DNIE", value=f"{maks_czas_na_dnie} MIN")

# NOWA SEKCJA: INSTRUKCJA TAKTYCZNA DLA NURKA
st.markdown("### 📝 Wytyczne do planu nurkowego (Wetnotes):")
st.success(f"📈 **Gaz dostępny na fazę denną:** {dostepny_gaz_bar} BAR (tyle możesz bezpiecznie wyoddychać przed powrotem).")

if turn_pressure_bar == rock_bottom_bar:
    st.error(f"📉 **MOMENT ODWRROTU (TURN PRESSURE): {turn_pressure_bar} BAR**. Twoje planowane nurkowanie zużywa cały dostępny gaz. Kończysz nurkowanie dokładnie w momencie wejścia na Rock Bottom!")
else:
    st.info(f"📉 **MOMENT ODWRROTU (TURN PRESSURE): {turn_pressure_bar} BAR**. Gdy Twój manometr wskaże tę wartość (lub minie {czas_na_dnie} min), zasygnalizuj partnerowi odwrót i skierujcie się do wyjścia.")

# --- DYNAMICZNE POWIADOMIENIA I ALERTS ---
st.write("---")
if glebokosc > mod_metry:
    st.error(f"☠️ **KRYTYCZNE ZAGROŻENIE!** Planowana głębokość ({glebokosc}m) przekracza MOD ({mod_metry:.1f}m). Ryzyko toksyczności tlenowej!")
elif jest_w_deco:
    st.warning(f"⚠️ **NURKOWANIE DEKOMPRESYJNE!** Przekroczłeś limit NDL. Maszyna Ski Way automatycznie dopisała **{czas_deco} min dekompresji**.")
else:
    st.info(f"ℹ️ Nurkowanie bezdekompresyjne. Maksymalny czas bez deko (NDL) na tej głębokości to: {lim_ndl} min.")

if dostepny_gaz_bar <= 0:
    st.error("🚨 **BŁĄD PLANOWANIA:** Brak gazu na powrót awaryjny! Zmień butlę na większą.")

# Ukryte szczegóły
with st.expander("🔍 Zobacz szczegółową anatomię powrotu awaryjnego:"):
    st.write(f"*   **Zużycie gazu na dnie w normalnych warunkach:** {zuzycie_denne_bar_min:.1f} BAR / minutę")
    st.write(f"*   **Planowane zużycie gazu przez {czas_na_dnie} min:** {planowane_zuzycie_bar} BAR")
    st.write(f"*   **Automatycznie przypisany czas Deco:** {czas_deco} minut")
    st.write(f"**Rozkład zużycia awaryjnego (dwie osoby):**")
    st.write(f"- Stres na dnie: {round(gaz_faza_stres)} litrów")
    st.write(f"- Droga w górę do 6m: {round(gaz_faza_wynurzanie_glebokie)} litrów")
    st.write(f"- Pobyt na 6m: {round(gaz_faza_przystanek)} litrów")
