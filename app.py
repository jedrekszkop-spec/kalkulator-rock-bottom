import streamlit as st
import math

st.set_page_config(page_title="Ski Way Diving Machine", page_icon="🤿", layout="centered")

st.markdown("""
<div style="background-color: #000000; padding: 25px; border-radius: 12px; text-align: center; margin-bottom: 25px;">
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

st.markdown("""
### 🧠 Czym jest Rock Bottom?
**Rock Bottom (Żelazna Rezerwa)** to krytyczne ciśnienie w butli, przy którym należy natychmiast rozpocząć wspólne wynurzanie z partnerem. 
*Algorytm Ski Way gwarantuje, że po przejściu całej procedury awaryjnej z partnerem, na powierzchni w butli zostanie Ci jeszcze **minimum 15 barów** do swobodnego oddychania.*
""")
st.write("---")

st.markdown("### Krok 1: Twój Sprzęt, Gaz i SAC")
col1, col2 = st.columns(2)
with col1:
    opcje_butli = {"7 L (Stage)": 7, "10 L": 10, "12 L (Standard)": 12, "15 L (Duża)": 15, "18 L (Bardzo duża)": 18, "2x10 L (Twins)": 20, "2x12 L (Twins)": 24}
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

ppo2_limit = 1.6
mod_metry = (ppo2_limit / fo2 - 1) * 10
st.info(f"✨ MOD ($PPO_2$=1.6): **{mod_metry:.1f} m**.")
st.write("---")

st.markdown("### Krok 2: Profil Planowanego Nurkowania")
col_prof1, col_prof2 = st.columns(2)
with col_prof1:
    glebokosc = st.number_input("Planowana głębokość (metry):", min_value=1, max_value=100, value=30, step=1)
    st.caption("*(Maksymalnie: 100 m)*")
with col_prof2:
    czas_na_dnie = st.number_input("Planowany czas na dnie (minuty):", min_value=1, max_value=60, value=15, step=1)
    st.caption("*(Maksymalnie: 60 min)*")

cisnienie_startowe = 200
p_dno = (glebokosc / 10) + 1
p_przystanek = (6 / 10) + 1
p_powierzchnia = 1.0
sac_awaryjne = sac_indywidualne * 2

gaz_norm_zanurzenie = (glebokosc / 15) * sac_indywidualne * ((p_powierzchnia + p_dno) / 2)
gaz_norm_dno = czas_na_dnie * sac_indywidualne * p_dno
zuzycie_zanurzenia_bar = math.ceil(gaz_norm_zanurzenie / pojemnosc_butli)
zuzycie_denne_bar = math.ceil((gaz_norm_zanurzenie + gaz_norm_dno) / pojemnosc_butli)
gaz_pozostaly_bar = cisnienie_startowe - zuzycie_denne_bar

gaz_stres = 2 * sac_awaryjne * p_dno
gaz_wyn1 = (((glebokosc - 6) / 9) * sac_awaryjne * ((p_dno + p_przystanek) / 2)) if glebokosc > 6 else 0
gaz_przystanek = 3 * sac_awaryjne * p_przystanek
gaz_wyn2 = 2 * sac_awaryjne * ((p_przystanek + p_powierzchnia) / 2)
total_awaryjny_litry = gaz_stres + gaz_wyn1 + gaz_przystanek + gaz_wyn2
rock_bottom_bar = math.ceil(((total_awaryjny_litry / pojemnosc_butli) + 15) / 10) * 10
rock_bottom_litry = rock_bottom_bar * pojemnosc_butli

st.write("---")
st.markdown("### 🎛️ Parametry Wyjściowe (Konsola Ski Way):")
r_col1, r_col2, r_col3 = st.columns(3)
with r_col1: st.metric(label="⏹️ WYMAGANY ROCK BOTTOM", value=f"{rock_bottom_bar} BAR", delta=f"{round(rock_bottom_litry)} L")
with r_col2: st.metric(label="📉 SAMO ZANURZENIE (Koszt)", value=f"{zuzycie_zanurzenia_bar} BAR", delta=f"{round(gaz_norm_zanurzenie)} L", delta_color="inverse")
with r_col3: st.metric(label="📉 MANOMETR PO DNIE", value=f"{max(0, gaz_pozostaly_bar)} BAR", delta=f"Zużyto: {zuzycie_denne_bar} bar")

if glebokosc > mod_metry: st.warning(f"⚠️ **OSTRZEŻENIE (MOD):** Przekroczono MOD ({mod_metry:.1f} m)!")
elif (zuzycie_denne_bar + rock_bottom_bar) > cisnienie_startowe: st.warning("⚠️ **PLAN PODWYŻSZONEGO RYZYKA:** Zabraknie gazu w butli 200 bar!")
else: st.success(f"👉 Wchodzisz z 200 bar. Wracasz przy {rock_bottom_bar} bar. Na brzegu zostaje minimum 15 bar.")

st.write("---")
st.markdown("### 🔍 Szczegółowe Rozbicie Litrów:")
with st.expander("Anatomia profilu solo:"):
    st.markdown(f"* Zanurzenie: {round(gaz_norm_zanurzenie)} L\n* Pobyt na dnie: {round(gaz_norm_dno)} L")
with st.expander("Anatomia powrotu awaryjnego (Rock Bottom):"):
    st.markdown(f"* Stres na dnie: {round(gaz_stres)} L\n* Wynurzenie do 6m: {round(gaz_wyn1)} L\n* Przystanek: {round(gaz_przystanek)} L\n* Wynurzenie z 6m: {round(gaz_wyn2)} L\n* Rezerwa techniczna: {round(15 * pojemnosc_butli)} L")
