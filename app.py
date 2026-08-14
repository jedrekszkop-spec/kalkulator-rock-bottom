import streamlit as st
import math

# 1. Konfiguracja aplikacji i nazwy w oknie przeglądarki
st.set_page_config(page_title="Ski Way Diving Machine", page_icon="🤿", layout="centered")

# --- OFICJALNE LOGOTYP W NAGŁÓWKU (HTML/CSS) ---
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

# --- SKRÓCONA DEFINICJA ---
st.markdown("""
### 🧠 Czym jest Rock Bottom?
**Rock Bottom (Żelazna Rezerwa)** to krytyczne ciśnienie w butli, przy którym należy natychmiast rozpocząć wspólne wynurzanie z partnerem. 
*Algorytm Ski Way gwarantuje, że po przejściu całej procedury awaryjnej z partnerem, na powierzchni w butli zostanie Ci jeszcze **minimum 15 barów** do swobodnego oddychania.*
""")
st.write("---")

# ==========================================
# KROK 1: SPRZĘT, GAZ I PARAMETRY (LINIOWO)
# ==========================================
st.markdown("### Krok 1: Twój Sprzęt, Gaz i SAC")

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
    wybrana_butla = st.selectbox("Pojemność Twojej butli:", list(opcje_butli.keys()), index=3)
    pojemnosc_butli = opcje_butli[wybrana_butla]
    
    typ_gazu = st.radio("Rodzaj używanego gazu:", ["Powietrze", "Nitrox"], horizontal=True)

with col2:
    sac_indywidualne = st.slider("Twoje zużycie powierzchniowe (SAC) [l/min]:", min_value=10, max_value=30, value=20, step=1)
    
    if typ_gazu == "Nitrox":
        nitrox_procent = st.slider("Zawartość tlenu (% O₂):", min_value=21, max_value=40, value=32, step=1)
        fo2 = nitrox_procent / 100
    else:
        fo2 = 0.21

# Obliczanie MOD dla stałego PPO2 = 1.6
ppo2_limit = 1.6
mod_metry = (ppo2_limit / fo2 - 1) * 10

if typ_gazu == "Nitrox":
    st.info(f"✨ Gaz: **Nitrox {int(fo2*100)}**. Maksymalna Głębokość Operacyjna (MOD) przy $PPO_2$=1.6 to: **{mod_metry:.1f} m**.")
else:
    st.info(f"✨ Gaz: **Powietrze**. Maksymalna Głębokość Operacyjna (MOD) przy $PPO_2$=1.6 to: **{mod_metry:.1f} m**.")

st.write("---")

# ==========================================
# KROK 2: PROFIL NURKOWANIA (Z BLOKADAMI)
# ==========================================
st.markdown("### Krok 2: Profil Planowanego Nurkowania")

col_prof1, col_prof2 = st.columns(2)
with col_prof1:
    glebokosc = st.number_input("Planowana głębokość (metry):", min_value=1, max_value=100, value=30, step=1)
    st.caption("*(Maksymalna głębokość możliwa do wybrania: 100 m)*")
with col_prof2:
    czas_na_dnie = st.number_input("Planowany czas na dnie (minuty):", min_value=1, max_value=60, value=15, step=1)
    st.caption("*(Maksymalny czas możliwy do wybrania: 60 min)*")

st.write("---")

# ==========================================
# MATEMATYKA PROFILU W TLE
# ==========================================
cisnienie_startowe = 200
p_dno = (glebokosc / 10) + 1
p_przystanek = (6 / 10) + 1
p_powierzchnia = 1.0
sac_awaryjne = sac_indywidualne * 2
gestosc_na_dnie = 1.29 * p_dno

# 1. Zużycie normalne solo
czas_zanurzenia = glebokosc / 15
p_sr_zanurzenia = (p_powierzchnia + p_dno) / 2
gaz_norm_zanurzenie = czas_zanurzenia * sac_indywidualne * p_sr_zanurzenia
gaz_norm_dno = czas_na_dnie * sac_indywidualne * p_dno

zuzycie_zanurzenia_bar = math.ceil(gaz_zan_t1 := gaz_norm_zanurzenie / pojemnosc_butli)
zuzycie_denne_bar = math.ceil((gaz_norm_zanurzenie + gaz_norm_dno) / pojemnosc_butli)
gaz_pozostaly_bar = cisnienie_startowe - zuzycie_denne_bar

# 2. Zużycie awaryjne (Rock Bottom)
gaz_faza_stres = 2 * sac_awaryjne * p_dno
gaz_faza_wynurzanie_glebokie = (((glebokosc - 6) / 9) * sac_awaryjne * ((p_dno + p_przystanek) / 2)) if glebokosc > 6 else 0
gaz_faza_przystanek = 3 * sac_awaryjne * p_przystanek
gaz_faza_wynurzanie_plytkie = 2 * sac_awaryjne * ((p_przystanek + p_powierzchnia) / 2)

calkowity_gaz_awaryjny_litry = gaz_faza_stres + gaz_faza_wynurzanie_glebokie + gaz_faza_przystanek + gaz_faza_wynurzanie_plytkie
czysty_powrot_bar = calkowity_gaz_awaryjny_litry / pojemnosc_butli

# Rock Bottom = Powrót + 15 bar technicznego zapasu na powierzchni
rock_bottom_bar = math.ceil((czysty_powrot_bar + 15) / 10) * 10
rock_bottom_litry = rock_bottom_bar * pojemnosc_butli
calkowity_wymagany_gaz_bar = zuzycie_denne_bar + rock_bottom_bar

# ==========================================
# KROK 3: KONSOLA STERUJĄCA I WYNIKI
# ==========================================
st.markdown("### 🎛️ Parametry Wyjściowe (Konsola Ski Way):")

r_col1, r_col2, r_col3 = st.columns(3)
with r_col1:
    st.metric(label="⏹️ WYMAGANY ROCK BOTTOM", value=f"{rock_bottom_bar} BAR", delta=f"{round(rock_bottom_litry)} litrów")
with r_col2:
    st.metric(label="📉 SAMO ZANURZENIE (Koszt)", value=f"{zuzycie_zanurzenia_bar} BAR", delta=f"{round(gaz_norm_zanurzenie)} litrów", delta_color="inverse")
with r_col3:
    st.metric(label="📉 MANOMETR PO DNIE", value=f"{max(0, gaz_pozostaly_bar)} BAR", delta=f"Zużyto na dnie: {zuzycie_denne_bar} bar")

# Łagodne, partnerskie ostrzeżenia
if glebokosc > mod_metry:
    st.warning(f"⚠️ **OSTRZEŻENIE O ZAGROŻENIU (MOD):** Głębokość ({glebokosc}m) przekracza limit operacyjny MOD ({mod_metry:.1f} m) dla tej mieszanki przy $PPO_2=1.6$!")
elif calkowity_wymagany_gaz_bar > cisnienie_startowe:
    st.warning(f"⚠️ **PLAN PODWYŻSZONEGO RYZYKA:** Łączne zapotrzebowanie na fazę denną oraz żelazną rezerwę przekracza pojemność butli 200 bar. Skróć czas lub weź większą butlę!")
else:
    st.success(f"👉 **Wytyczne:** Startujesz z 200 bar. Gdy manometr wskaże **{rock_bottom_bar} bar** – natychmiast wracasz. Po wyjściu z partnerem na powierzchni zostanie bezpieczne **minimum 15 barów**.")

if p_dno * 1.29 > 5.2 and glebokosc <= mod_metry:
    st.warning(f"⚠️ **Uwaga:** Gęstość gazu na dnie wynosi {(p_dno * 1.29):.1f} g/l. Opór oddechowy automatu będzie nieco większy.")

# ==========================================
# KROK 4: ROZWIJANA ANATOMIA LITRÓW
# ==========================================
st.write("---")
st.markdown("### 🔍 Szczegółowe Rozbicie Litrów (Podsumowanie profilu):")

with st.expander("Zobacz anatomię CAŁEGO nurkowania (Planowany profil solo):"):
    st.markdown(f"""
    *   📉 **Zanurzenie na {glebokosc}m:** {round(gaz_norm_zanurzenie)} litrów *(Czas: {(glebokosc/15):.1f} min)*
    *   ⏱️ **Pobyt na dnie ({czas_na_dnie} min):** {round(gaz_norm_dno)} litrów
    *   **Łącznie faza denna:** {round(gaz_norm_zanurzenie + gaz_norm_dno)} litrów (~{zuzycie_denne_bar} bar).
    """)

with st.expander("Zobacz szczegółową anatomię powrotu awaryjnego (Rock Bottom):"):
    st.markdown(f"""
    *   **Faza 1 (Stres na dnie):** {round(gaz_faza_stres)} litrów *(2 minuty)*
    *   **Faza 2 (Wynurzenie do 6m):** {round(gaz_faza_wynurzanie_glebokie)} litrów *(Prędkość 9 m/min)*
    *   **Faza 3 (Przystanek na 6m):** {round(gaz_faza_przystanek)} litrów *(3 minuty)*
    *   **Faza 4 (Wynurzenie do powierzchni):** {round(gaz_faza_wynurzanie_plytkie)} litrów *(2 minuty)*
    *   🛡️ **Techniczna rezerwa końcowa:** {round(15 * pojemnosc_butli)} litrów *(15 barów na powierzchni)*
    """)
