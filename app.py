import streamlit as st
import math

st.set_page_config(page_title="Ski Way Diving Machine", page_icon="🤿", layout="centered")

st.title("🤿 Ski Way Diving Machine")
st.subheader("Kompletny planer profili nurkowych i balansowania gazu")
st.write("---")

st.markdown("""
### 🧠 Czym jest Rock Bottom?
**Rock Bottom (Żelazna Rezerwa)** to minimalne ciśnienie w butli, przy którym należy natychmiast rozpocząć wspólne wynurzanie z partnerem. 
""")
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
    ppo2_limit = 1.6
    mod_metry = (ppo2_limit / fo2 - 1) * 10

    st.write("---")
    st.markdown("### Krok 2: Profil Planowanego Nurkowania")
    col_prof1, col_prof2 = st.columns(2)
    with col_prof1: glebokosc = st.number_input("Planowana głębokość (m):", 1, 100, 30, step=1)
    with col_prof2: czas_na_dnie = st.number_input("Planowany czas na dnie (min):", 1, 60, 15, step=1)

    cisnienie_startowe = 200

with tab2:
    st.markdown("### Dostosuj parametry fizjologiczne")
    sac_indywidualne = st.slider("Twoje standardowe zużycie (SAC) [l/min]:", 10, 30, 20)

p_dno = (glebokosc / 10) + 1
p_przystanek = (6 / 10) + 1
p_powierzchnia = 1.0

# Obliczenia Fazy Dennej Solo
gaz_zan = (glebokosc / 15) * sac_indywidualne * ((p_powierzchnia + p_dno) / 2)
gaz_dno = czas_na_dnie * sac_indywidualne * p_dno
zuzycie_denne_bar = math.ceil((gaz_zan + gaz_dno) / pojemnosc_butli)
gaz_pozostaly_bar = cisnienie_startowe - zuzycie_denne_bar

# Obliczenia Rock Bottom + 15 bar technicznych
sac_awaryjne = sac_indywidualne * 2
g_stres = 2 * sac_awaryjne * p_dno
g_wyn1 = (((glebokosc - 6) / 9) * sac_awaryjne * ((p_dno + p_przystanek) / 2)) if glebokosc > 6 else 0
g_przystanek = 3 * sac_awaryjne * p_przystanek
g_wyn2 = 2 * sac_awaryjne * ((p_przystanek + p_powierzchnia) / 2)
rock_bottom_bar = math.ceil((((g_stres + g_wyn1 + g_przystanek + g_wyn2) / pojemnosc_butli) + 15) / 10) * 10

st.write("---")
st.markdown("### 🎛️ Parametry Wyjściowe (Konsola Ski Way):")
res_col1, res_col2 = st.columns(2)
res_col1.metric("⏹️ WYMAGANY ROCK BOTTOM", f"{rock_bottom_bar} BAR")
res_col2.metric("📉 CIŚNIENIE PO FAZIE DENNEJ", f"{max(0, gaz_pozostaly_bar)} BAR")
