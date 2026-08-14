import streamlit as st
import math

# 1. Konfiguracja aplikacji i nazwy w oknie przeglądarki
st.set_page_config(page_title="Ski Way Diving Machine", page_icon="🤿", layout="centered")

# Nagłówek aplikacji z Twoją własną nazwą
st.title("🤿 Ski Way Diving Machine")
st.subheader("Automatyczny planer profili i rezerw dekompresyjnych")
st.write("---")

# Podział na przejrzyste zakładki
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
        wybrana_butla_tekst = st.selectbox("Pojemność butli:", list(opcje_butli.keys()), index=2)
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
        czas_na_dnie = st.number_input("Planowany czas na dnie (minuty):", min_value=1, max_value=90, value=15, step=1)

    # --- BAZA DANYCH NDL (Limity bezdekompresyjne dla danych głębokości) ---
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

    # Standardowe założenia w tle
    cisnienie_startowe = 200
    gestosc_na_dnie = 1.29 * ((glebokosc / 10) + 1)

with tab2:
    st.markdown("### Dostosuj parametry fizjologiczne")
    sac_indywidualne = st.slider("Twoje standardowe zużycie (SAC) [l/min]:", min_value=10, max_value=30, value=20, step=1)
    ppo2_custom = st.slider("Limit ciśnienia parcjalnego tlenu (PPO₂):", min_value=1.2, max_value=1.6, value=1.4, step=0.1)
    
    # Przeliczenie MOD na podstawie wybranego O2 i PPO2
    mod_metry = (ppo2_custom / fo2 - 1) * 10

# --- AUTOMATYCZNY SILNIK OBLICZENIOWY ROCK BOTTOM ---
sac_awaryjne = sac_indywidualne * 2
p_dno = (glebokosc / 10) + 1
p_przystanek = (6 / 10) + 1
p_powierzchnia = 1.0

# 1. Stres na dnie (2 min)
gaz_faza_stres = 2 * sac_awaryjne * p_dno

# 2. Wynurzenie z dna do 6m (prędkość 9 m/min)
if glebokosc > 6:
    dystans_faza1 = glebokosc - 6
    czas_faza1 = dystans_faza1 / 9
    p_sr_faza1 = (p_dno + p_przystanek) / 2
    gaz_faza_wynurzanie_glebokie = czas_faza1 * sac_awaryjne * p_sr_faza1
else:
    gaz_faza_wynurzanie_glebokie = 0

# 3. Pobyt na 6 metrach: Standardowy przystanek bezpieczeństwa (3 min) + AUTOMATYCZNE DECO
calkowity_czas_na_6m = 3 + czas_deco
gaz_faza_przystanek = calkowity_czas_na_6m * sac_awaryjne * p_przystanek

# 4. Wynurzenie z 6m do powierzchni (2 min)
czas_faza2 = 6 / 3
p_sr_faza2 = (p_przystanek + p_powierzchnia) / 2
gaz_faza_wynurzanie_plytkie = czas_faza2 * sac_awaryjne * p_sr_faza2

# Końcowe sumowanie barów (zaokrąglone do 10 bar)
calkowity_gaz_litry = gaz_faza_stres + gaz_faza_wynurzanie_glebokie + gaz_faza_przystanek + gaz_faza_wynurzanie_plytkie
rock_bottom_bar = math.ceil((calkowity_gaz_litry / pojemnosc_butli) / 10) * 10
dostepny_gaz_bar = cisnienie_startowe - rock_bottom_bar


# --- SEKCJA WYNIKÓW I RAPORTU ---
st.write("---")
st.markdown("### 📊 Raport Bezpieczeństwa Profilu:")

# Wizualne karty główne
res_col1, res_col2 = st.columns(2)
with res_col1:
    st.metric(label="🚨 ROCK BOTTOM (Zapas awaryjny)", value=f"{rock_bottom_bar} BAR")
with res_col2:
    if dostepny_gaz_bar > 0:
        st.metric(label="🟢 GAZ NA FAZĘ DENNĄ", value=f"{dostepny_gaz_bar} BAR")
    else:
        st.metric(label="❌ GAZ NA FAZĘ DENNĄ", value="BRAK")

# --- DYNAMICZNE POWIADOMIENIA I ALERTY ---
if glebokosc > mod_metry:
    st.error(f"☠️ **KRYTYCZNE ZAGROŻENIE!** Planowana głębokość ({glebokosc}m) przekracza MOD ({mod_metry:.1f}m). Ryzyko toksyczności tlenowej!")
elif jest_w_deco:
    st.warning(f"⚠️ **NURKOWANIE DEKOMPRESYJNE!** Przekroczyłeś limit NDL ({lim_ndl} min) na tej głębokości. Agent Ski Way automatycznie dopisał **{czas_deco} min obowiązkowej dekompresji** do planu powrotu. Twój Rock Bottom wzrósł!")
else:
    st.info(f"ℹ️ Nurkowanie bezpieczne (Bezdekompresyjne). Twój limit czasu na tej głębokości wynosił: {lim_ndl} min. Wykonujesz tylko standardowy przystanek 3 min.")

if gestosc_na_dnie > 5.2 and glebokosc <= mod_metry:
    st.warning(f"💨 **GĘSTOŚĆ GAZU OSTRZEŻENIE:** Na głębokości {glebokosc}m gęstość wynosi {gestosc_na_dnie:.1f} g/l. Oddychanie będzie cięższe.")

if dostepny_gaz_bar <= 0:
    st.error("🚨 **BŁĄD PLANOWANIA:** Wymagany gaz awaryjny przekracza pojemność butli 200 bar! Skróć czas nurkowania lub wybierz większą butlę (np. Twins).")

# Ukryte szczegóły
with st.expander("🔍 Zobacz szczegółową anatomię powrotu awaryjnego:"):
    st.write(f"*   **Limit NDL dla tej głębokości:** {lim_ndl} minut")
    st.write(f"*   **Automatycznie przypisany czas Deco:** {czas_deco} minut")
    st.write(f"*   **Łączny czas wiszenia na 6 metrach (Przystanek + Deco):** {calkowity_czas_na_6m} minut")
    st.write(f"**Rozkład zużycia awaryjnego przez Ski Way Machine:**")
    st.write(f"- Stres na dnie: {round(gaz_faza_stres)} litrów")
    st.write(f"- Droga w górę do 6m: {round(gaz_faza_wynurzanie_glebokie)} litrów")
    st.write(f"- Pobyt na 6m: {round(gaz_faza_przystanek)} litrów")
    st.write(f"- Wyjście z 6m na powierzchnię: {round(gaz_faza_wynurzanie_plytkie)} litrów")
