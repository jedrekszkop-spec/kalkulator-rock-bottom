import streamlit as st
import math

# 1. Konfiguracja i Nazwa Aplikacji w oknie przeglądarki
st.set_page_config(page_title="DeepPlan – Asystent Nurkowy", page_icon="🤿", layout="centered")

# Nowy, czysty nagłówek
st.title("🤿 DeepPlan")
st.subheader("Twój osobisty asystent planowania i bezpieczeństwa")
st.write("---")

# Podział na zakładki dla maksymalnej przejrzystości
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
    st.markdown("### Krok 2: Profil Nurkowania")
    
    # Główne parametry wejściowe profilu
    glebokosc = st.number_input("Planowana głębokość (metry):", min_value=1, max_value=50, value=30, step=1)
    
    # Wybór czy nurkowanie jest bezdekompresyjne czy z deco
    ma_deco = st.checkbox("Planuję wejść w dekompresję (Deco Stop)")
    if ma_deco:
        czas_deco = st.number_input("Łączny czas przystanków dekompresyjnych (minuty):", min_value=1, max_value=60, value=5)
    else:
        czas_deco = 0

    # --- OBLICZENIA LOGICZNE (W TLE) ---
    cisnienie_startowe = 200
    
    # 1. MOD i PPO2
    ppo2_limit = 1.4
    mod_metry = (ppo2_limit / fo2 - 1) * 10
    
    # 2. Limit NDL (Tylko informacyjnie dla Powietrza)
    if glebokosc <= 10: ndl_tekst = "Brak limitu (100+ min)"
    elif glebokosc <= 12: ndl_tekst = "ok. 120 min"
    elif glebokosc <= 15: ndl_tekst = "ok. 75 min"
    elif glebokosc <= 18: ndl_tekst = "ok. 50 min"
    elif glebokosc <= 22: ndl_tekst = "ok. 35 min"
    elif glebokosc <= 25: ndl_tekst = "ok. 25 min"
    elif glebokosc <= 30: ndl_tekst = "ok. 20 min"
    elif glebokosc <= 35: ndl_tekst = "ok. 14 min"
    elif glebokosc <= 40: ndl_tekst = "ok. 9 min"
    else: ndl_tekst = "Poniżej 5 min!"

    # 3. Gęstość gazu (Gas Density)
    # Gęstość powietrza na powierzchni to ok. 1.2 g/l. Nitrox jest minimalnie cięższy, ale przyjmujemy średnią fizyczną.
    gestosc_na_dnie = 1.29 * ((glebokosc / 10) + 1)

with tab2:
    st.markdown("### Dostosuj parametry fizjologiczne")
    # Przeniesione tutaj, aby nie zaciemniać głównego widoku
    sac_indywidualne = st.slider("Twoje standardowe zużycie (SAC) [l/min]:", min_value=10, max_value=30, value=20, step=1)
    ppo2_custom = st.slider("Limit ciśnienia parcjalnego tlenu (PPO₂):", min_value=1.2, max_value=1.6, value=1.4, step=0.1)
    
    # Przeliczenie MOD na podstawie customowego PPO2
    mod_metry = (ppo2_custom / fo2 - 1) * 10

# --- SILNIK OBLICZENIOWY ROCK BOTTOM ---
sac_awaryjne = sac_indywidualne * 2
p_dno = (glebokosc / 10) + 1
p_przystanek = (6 / 10) + 1
p_powierzchnia = 1.0

# Obliczanie fazowe litrów
gaz_faza_stres = 2 * sac_awaryjne * p_dno

if glebokosc > 6:
    dystans_faza1 = glebokosc - 6
    czas_faza1 = dystans_faza1 / 9
    p_sr_faza1 = (p_dno + p_przystanek) / 2
    gaz_faza_wynurzanie_glebokie = czas_faza1 * sac_awaryjne * p_sr_faza1
else:
    gaz_faza_wynurzanie_glebokie = 0

# Przystanek bezpieczeństwa (3 min) + ewentualny dopisany czas dekompresji
calkowity_czas_na_6m = 3 + czas_deco
gaz_faza_przystanek = calkowity_czas_na_6m * sac_awaryjne * p_przystanek

czas_faza2 = 6 / 3
p_sr_faza2 = (p_przystanek + p_powierzchnia) / 2
gaz_faza_wynurzanie_plytkie = czas_faza2 * sac_awaryjne * p_sr_faza2

calkowity_gaz_litry = gaz_faza_stres + gaz_faza_wynurzanie_glebokie + gaz_faza_przystanek + gaz_faza_wynurzanie_plytkie
rock_bottom_bar = math.ceil((calkowity_gaz_litry / pojemnosc_butli) / 10) * 10
dostepny_gaz_bar = cisnienie_startowe - rock_bottom_bar


# --- SEKCJA WYNIKÓW (Niezwykle przejrzysta) ---
st.write("---")
st.markdown("### 📊 Raport Bezpieczeństwa:")

# Duże, czytelne ramki z najważniejszymi liczbami
res_col1, res_col2 = st.columns(2)
with res_col1:
    st.metric(label="🚨 ROCK BOTTOM (Zapas awaryjny)", value=f"{rock_bottom_bar} BAR")
with res_col2:
    if dostepny_gaz_bar > 0:
        st.metric(label="🟢 GAZ NA FAZĘ DENNĄ", value=f"{dostepny_gaz_bar} BAR")
    else:
        st.metric(label="❌ GAZ NA FAZĘ DENNĄ", value="BRAK")

# Ważne komunikaty i ostrzeżenia pod spodem
if glebokosc > mod_metry:
    st.error(f"☠️ **PRZEKROCZONO MOD!** Maksymalna głębokość dla tego gazu to **{mod_metry:.1f} m**. Zmniejsz głębokość lub zmniejsz % tlenu!")
elif gestosc_na_dnie > 5.2:
    st.warning(f"⚠️ **GĘSTY GAZ!** Gęstość gazu na dnie wynosi **{gestosc_na_dnie:.1f} g/l** (Norma to 5.2). Powietrze/Nitrox na tej głębokości utrudnia oddychanie i nasila narkozę azotową.")
else:
    st.info(f"ℹ️ Szacowany limit bezdekompresyjny (NDL) dla tej głębokości wynosi: **{ndl_tekst}**.")

if dostepny_gaz_bar <= 0:
    st.error("⚠️ **NIEBEZPIECZNY PLAN!** Sam powrót awaryjny z partnerem wymaga więcej gazu niż mieści butla 200 bar. Weź większą butlę!")

# Rozwijane menu z technicznymi detalami
with st.expander("🔍 Zobacz szczegóły techniczne i podział litrów:"):
    st.write(f"*   **Maksymalna Głębokość Operacyjna (MOD):** {mod_metry:.1f} m")
    st.write(f"*   **Gęstość gazu na dnie:** {gestosc_na_dnie:.1f} g/l")
    st.write(f"**Zużycie w litrach podczas awarii:**")
    st.write(f"- Rozwiązanie problemu na dnie (2 min): {round(gaz_faza_stres)} l")
    st.write(f"- Wynurzenie do strefy przystanków: {round(gaz_faza_wynurzanie_glebokie)} l")
    st.write(f"- Pobyt na 6 metrach (Przystanek + Deco): {round(gaz_faza_przystanek)} l")
    st.write(f"- Wynurzenie z 6m do powierzchni: {round(gaz_faza_wynurzanie_plytkie)} l")
    st.write(f"**Łącznie potrzebny gaz awaryjny:** {round(calkowity_gaz_litry)} litrów.")
