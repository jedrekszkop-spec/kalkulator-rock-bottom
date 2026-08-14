import streamlit as st
import math

# 1. Konfiguracja aplikacji i nazwy w oknie przeglądarki
st.set_page_config(page_title="Ski Way Diving Machine", page_icon="🤿", layout="centered")

# --- NOWOŚĆ: IMPLEMENTACJA OFICJALNEGO LOGOTYPU W NAGŁÓWKU (HTML/CSS) ---
st.markdown("""
<div style="background-color: #000000; padding: 25px; border-radius: 12px; text-align: center; margin-bottom: 25px; box-shadow: 0px 4px 15px rgba(0,0,0,0.3);">
    <h1 style="color: #FFFFFF; font-family: 'Helvetica Neue', Arial, sans-serif; font-weight: 900; letter-spacing: 6px; margin: 0; font-size: 3rem;">
        SKIW<span style="color: #FF4B4B; font-size: 3.2rem; position: relative; top: -2px;">▲</span>Y
    </h1>
    <p style="color: #A0A0A0; font-family: 'Courier New', Courier, monospace; font-weight: bold; letter-spacing: 4px; margin: 5px 0 0 0; font-size: 1rem;">
        DIVING MACHINE
    </p>
</div>
""", unsafe_html=True)

st.subheader("Kompletny planer profili nurkowych i limitów bezpieczeństwa")
st.write("---")

# --- SKRÓCONA DEFINICJA NA GÓRZE ---
st.markdown("""
### 🧠 Czym jest Rock Bottom?
**Rock Bottom (Żelazna Rezerwa)** to krytyczne ciśnienie w butli, przy którym należy natychmiast rozpocząć wspólne wynurzanie z partnerem. 
*Algorytm Ski Way gwarantuje, że po przejściu całej procedury awaryjnej z partnerem, na powierzchni w butli zostanie Ci jeszcze **minimum 15 barów** do swobodnego oddychania.*
""")
st.write("---")

# --- GLOBALNA LISTA BUTLI DO WYBORU ---
opcje_butli = {
    "7 L (Stage)": 7,
    "10 L": 10,
    "12 L (Standard)": 12,
    "15 L (Duża)": 15,
    "18 L (Bardzo duża)": 18,
    "2x10 L (Twins)": 20,
    "2x12 L (Twins)": 24
}

# Podział na TRZY zakładki
tab1, tab2, tab3 = st.tabs(["📋 Planowanie Nurkowania", "⏱️ Szybki Limit Czasowy", "🔬 Zaawansowane Parametry"])

# Odczyt parametrów zaawansowanych
with tab3:
    st.markdown("### Dostosuj parametry fizjologiczne")
    sac_indywidualne = st.slider("Twoje standardowe zużycie (SAC) [l/min]:", min_value=10, max_value=30, value=20, step=1)

# Stałe założenia fizyczne
cisnienie_startowe = 200
ppo2_limit = 1.6
p_przystanek = (6 / 10) + 1
p_powierzchnia = 1.0


# ==========================================
# ZAKŁADKA 1: PLANOWANIE NURKOWANIA
# ==========================================
with tab1:
    st.markdown("### Krok 1: Twój Sprzęt i Gaz")
    col1, col2 = st.columns(2)
    with col1:
        wybrana_butla_t1 = st.selectbox("Pojemność butli (Tab 1):", list(opcje_butli.keys()), index=3, key="butla_t1")
        pojemnosc_butli_t1 = opcje_butli[wybrana_butla_t1]
    with col2:
        typ_gazu_t1 = st.radio("Rodzaj gazu (Tab 1):", ["Powietrze", "Nitrox"], horizontal=True, key="gas_t1")

    if typ_gazu_t1 == "Nitrox":
        nitrox_procent_t1 = st.slider("Zawartość tlenu (% O₂):", min_value=21, max_value=40, value=32, step=1, key="nitrox_t1")
        fo2_t1 = nitrox_procent_t1 / 100
    else:
        fo2_t1 = 0.21

    mod_t1 = (ppo2_limit / fo2_t1 - 1) * 10
    st.info(f"✨ MOD ($PPO_2$=1.6): **{mod_t1:.1f} m**.")

    st.write("---")
    st.markdown("### Krok 2: Profil Planowanego Nurkowania")
    col_prof1, col_prof2 = st.columns(2)
    with col_prof1:
        glebokosc_t1 = st.number_input("Planowana głębokość (metry):", min_value=1, max_value=100, value=30, step=1, key="gl_t1")
        st.caption("*(Maksymalnie: 100 m)*")
    with col_prof2:
        czas_na_dnie_t1 = st.number_input("Planowany czas na dnie (minuty):", min_value=1, max_value=60, value=15, step=1, key="cz_t1")
        st.caption("*(Maksymalnie: 60 min)*")

    # Obliczenia Fazy Dennej Solo (Tab 1)
    p_dno_t1 = (glebokosc_t1 / 10) + 1
    p_sr_zan_t1 = (p_powierzchnia + p_dno_t1) / 2
    gaz_zan_t1 = (glebokosc_t1 / 15) * sac_indywidualne * p_sr_zan_t1
    gaz_dno_t1 = czas_na_dnie_t1 * sac_indywidualne * p_dno_t1
    zuzycie_denne_bar_t1 = math.ceil((gaz_zan_t1 + gaz_dno_t1) / pojemnosc_butli_t1)
    gaz_pozostaly_bar_t1 = cisnienie_startowe - zuzycie_denne_bar_t1

    # Obliczenia Rock Bottom (Tab 1)
    sac_awaryjne = sac_indywidualne * 2
    gaz_stres_t1 = 2 * sac_awaryjne * p_dno_t1
    gaz_wyn1_t1 = ((glebokosc_t1 - 6) / 9) * sac_awaryjne * ((p_dno_t1 + p_przystanek) / 2) if glebokosc_t1 > 6 else 0
    gaz_przystanek_t1 = 3 * sac_awaryjne * p_przystanek
    gaz_wyn2_t1 = 2 * sac_awaryjne * ((p_przystanek + p_powierzchnia) / 2)
    
    total_awaryjny_litry_t1 = gaz_stres_t1 + gaz_wyn1_t1 + gaz_przystanek_t1 + gaz_wyn2_t1
    rock_bottom_bar_t1 = math.ceil(((total_awaryjny_litry_t1 / pojemnosc_butli_t1) + 15) / 10) * 10

    # Wyniki Tab 1
    st.write("---")
    st.markdown("### 🎛️ Parametry Wyjściowe (Konsola Ski Way):")
    r_col1, r_col2 = st.columns(2)
    with r_col1:
        st.metric(label="⏹️ WYMAGANY ROCK BOTTOM", value=f"{rock_bottom_bar_t1} BAR")
    with r_col2:
        st.metric(label="📉 MANOMETR PO FAZIE DENNEJ", value=f"{max(0, gaz_pozostaly_bar_t1)} BAR")

    if glebokosc_t1 > mod_t1:
        st.warning(f"⚠️ **OSTRZEŻENIE (MOD):** Głębokość przekracza MOD ({mod_t1:.1f} m)!")
    elif gaz_pozostaly_bar_t1 < rock_bottom_bar_t1:
        st.warning(f"⚠️ **PLAN PODWYŻSZONEGO RYZYKA:** Na dnie zostanie Ci za mało gazu awaryjnego ({gaz_pozostaly_bar_t1} bar vs {rock_bottom_bar_t1} bar Rock Bottom)!")
    else:
        st.success(f"👉 Wytyczne: Po fazie dennej zostanie {gaz_pozostaly_bar_t1} bar. Bezpiecznie wracasz przy {rock_bottom_bar_t1} bar.")


# ==========================================
# ZAKŁADKA 2: SZYBKI LIMIT CZASOWY
# ==========================================
with tab2:
    st.markdown("### ⏱️ Automatyczne Wyliczanie Bezpiecznego Czasu")
    st.write("Wpisz parametry, a maszyna od razu powie Ci, na ile minut starczy Ci gazu przed wejściem na rezerwę.")
    
    col_t2_1, col_t2_2 = st.columns(2)
    with col_t2_1:
        wybrana_butla_t2 = st.selectbox("Pojemność butli (Tab 2):", list(opcje_butli.keys()), index=3, key="butla_t2")
        pojemnosc_butli_t2 = opcje_butli[wybrana_butla_t2]
    with col_t2_2:
        typ_gazu_t2 = st.radio("Rodzaj gazu (Tab 2):", ["Powietrze", "Nitrox"], horizontal=True, key="gas_t2")

    if typ_gazu_t2 == "Nitrox":
        nitrox_procent_t2 = st.slider("Zawartość tlenu (% O₂):", min_value=21, max_value=40, value=32, step=1, key="nitrox_t2")
        fo2_t2 = nitrox_procent_t2 / 100
    else:
        fo2_t2 = 0.21

    mod_t2 = (ppo2_limit / fo2_t2 - 1) * 10
    st.info(f"✨ MOD ($PPO_2$=1.6): **{mod_t2:.1f} m**.")

    glebokosc_t2 = st.number_input("Wpisz głębokość docelową (metry):", min_value=1, max_value=100, value=30, step=1, key="gl_t2")
    st.caption("*(Maksymalnie: 100 m)*")

    # Obliczenia Rock Bottom dla głębokości z Tab 2
    p_dno_t2 = (glebokosc_t2 / 10) + 1
    gaz_stres_t2 = 2 * sac_awaryjne * p_dno_t2
    gaz_wyn1_t2 = ((glebokosc_t2 - 6) / 9) * sac_awaryjne * ((p_dno_t2 + p_przystanek) / 2) if glebokosc_t2 > 6 else 0
    gaz_przystanek_t2 = 3 * sac_awaryjne * p_przystanek
    gaz_wyn2_t2 = 2 * sac_awaryjne * ((p_przystanek + p_powierzchnia) / 2)
    
    total_awaryjny_litry_t2 = gaz_stres_t2 + gaz_wyn1_t2 + gaz_przystanek_t2 + gaz_wyn2_t2
    rock_bottom_bar_t2 = math.ceil(((total_awaryjny_litry_t2 / pojemnosc_butli_t2) + 15) / 10) * 10

    # Obliczenie maksymalnego bezpiecznego czasu
    gaz_zan_litry_t2 = (glebokosc_t2 / 15) * sac_indywidualne * ((p_powierzchnia + p_dno_t2) / 2)
    gaz_dostepny_dno_bar_t2 = cisnienie_startowe - rock_bottom_bar_t2
    gaz_dostepny_dno_litry_t2 = gaz_dostepny_dno_bar_t2 * pojemnosc_butli_t2
    gaz_czysty_na_dnie_litry_t2 = gaz_dostepny_dno_litry_t2 - gaz_zan_litry_t2
    zuzycie_minutowe_t2 = sac_indywidualne * p_dno_t2

    if gaz_czysty_na_dnie_litry_t2 > 0 and gaz_dostepny_dno_bar_t2 > 0:
        maks_czas_t2 = math.floor(gaz_czysty_na_dnie_litry_t2 / zuzycie_minutowe_t2)
        if maks_czas_t2 < 0: maks_czas_t2 = 0
    else:
        maks_czas_t2 = 0

    # Wyniki Tab 2
    st.write("---")
    st.markdown("### 🎛️ Wynik Automatyczny:")
    t2_col1, t2_col2 = st.columns(2)
    with t2_col1:
        st.metric(label="⏱️ MAKSYMALNY CZAS NA DNIE", value=f"{maks_czas_t2} MIN")
    with t2_col2:
        st.metric(label="⏹️ ŻELAZNA REZERWA (Rock Bottom)", value=f"{rock_bottom_bar_t2} BAR")

    if glebokosc_t2 > mod_t2:
        st.warning(f"⚠️ **OSTRZEŻENIE (MOD):** Głębokość przekracza MOD ({mod_t2:.1f} m)!")
    elif gaz_dostepny_dno_bar_t2 <= 0:
        st.warning("⚠️ **PLAN PODWYŻSZONEGO RYZYKA:** Ta butla jest za mała! Sam powrót awaryjny wymaga więcej niż 200 bar!")
    else:
        st.success(f"👉 **Wytyczne Ski Way:** Na głębokości {glebokosc_t2}m możesz spędzić maksymalnie **{maks_czas_t2} minut**. Po tym czasie Twój manometr osiągnie {rock_bottom_bar_t2} bar i musisz wracać.")


# ==========================================
# SZCZEGÓŁOWA ANATOMIA NA SAMYM DOLE STRONY
# ==========================================
st.write("---")
st.markdown("### 🔍 Szczegółowe Rozbicie Litrów (Dla aktywnego profilu z Zakładki 1):")

with st.expander("Zobacz anatomię CAŁEGO nurkowania (Planowany profil solo):"):
    st.markdown(f"""
    *   📉 **Zanurzenie na {glebokosc_t1}m:** {round(gaz_zan_t1)} litrów
    *   ⏱️ **Pobyt na dnie ({czas_na_dnie_t1} min):** {round(gaz_dno_t1)} litrów
    *   **Łącznie faza denna:** {round(gaz_zan_t1 + gaz_dno_t1)} litrów (~{zuzycie_denne_bar_t1} bar).
    """)

with st.expander("Zobacz szczegółową anatomię powrotu awaryjnego (Rock Bottom):"):
    st.markdown(f"""
    *   **Faza 1 (Stres na dnie):** {round(gaz_stres_t1)} litrów *(2 minuty)*
    *   **Faza 2 (Wynurzenie do 6m):** {round(gaz_wyn1_t1)} litrów *(Prędkość 9 m/min)*
    *   **Faza 3 (Przystanek na 6m):** {round(gaz_przystanek_t1)} litrów *(3 minuty)*
    *   **Faza 4 (Wynurzenie do powierzchni):** {round(gaz_wyn2_t1)} litrów *(2 minuty)*
    *   🛡️ **Rezerwa końcowa:** {round(15 * pojemnosc_butli_t1)} litrów *(15 barów na powierzchni)*
    """)

