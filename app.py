import streamlit as st
import math

# 1. Konfiguracja aplikacji i nazwy w oknie przeglądarki
st.set_page_config(page_title="Ski Way Diving Machine", page_icon="🤿", layout="centered")

# --- IMPLEMENTACJA OFICJALNEGO LOGOTYPU W NAGŁÓWKU (HTML/CSS) ---
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

st.subheader("Kompletny planer profili nurkowych i balansowania gazu")
st.write("---")

# --- SKRÓCONA DEFINICJA NA GÓRZE ---
st.markdown("""
### 🧠 Czym jest Rock Bottom?
**Rock Bottom (Żelazna Rezerwa)** to minimalne ciśnienie w butli, przy którym należy natychmiast rozpocząć wspólne wynurzanie z partnerem. 
*Algorytm Ski Way wylicza to zapotrzebowanie awaryjne i porównuje je z gazem, który realnie zostanie Ci w butli po zakończeniu Twojej fazy dennej (startując z 200 bar).*
""")
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

    # Dynamiczny suwak dla Nitroxu (Wybór od 21% do 40%)
    if typ_gazu == "Nitrox":
        nitrox_procent = st.slider("Zawartość tlenu (% O₂):", min_value=21, max_value=40, value=32, step=1)
        fo2 = nitrox_procent / 100
    else:
        fo2 = 0.21

    # --- FUNKCJA MOD (Stałe PPO2 = 1.6) ---
    ppo2_limit = 1.6
    mod_metry = (ppo2_limit / fo2 - 1) * 10

    if typ_gazu == "Zwykłe powietrze" or typ_gazu == "Powietrze":
        st.info(f"✨ Gaz: **Powietrze**. Maksymalna Głębokość Operacyjna (MOD) dla stałego $PPO_2$=1.6 wynosi: **{mod_metry:.1f} m**.")
    else:
        st.info(f"✨ Gaz: **Nitrox {int(fo2*100)}**. Maksymalna Głębokość Operacyjna (MOD) dla stałego $PPO_2$=1.6 wynosi: **{mod_metry:.1f} m**.")

    st.write("---")
    st.markdown("### Krok 2: Profil Planowanego Nurkowania")
    
    col_prof1, col_prof2 = st.columns(2)
    with col_prof1:
        glebokosc = st.number_input("Planowana głębokość (metry):", min_value=1, max_value=100, value=30, step=1)
        st.caption("*(Maksymalna głębokość możliwa do wybrania: 100 m)*")
    with col_prof2:
        czas_na_dnie = st.number_input("Planowany czas na dnie (minuty):", min_value=1, max_value=60, value=15, step=1)
        st.caption("*(Maksymalny czas możliwy do wybrania: 60 min)*")

    cisnienie_startowe = 200
    gestosc_na_dnie = 1.29 * ((glebokosc / 10) + 1)

with tab2:
    st.markdown("### Dostosuj parametry fizjologiczne")
    sac_indywidualne = st.slider("Twoje standardowe zużycie (SAC) [l/min]:", min_value=10, max_value=30, value=20, step=1)

# --- MATEMATYKA FIZYCZNA PROFILU NURKOWANIA ---
p_dno = (glebokosc / 10) + 1
p_przystanek = (6 / 10) + 1
p_powierzchnia = 1.0

# --- KROK A: OBLICZAMY ILE POWIETRZA ZUŻYJESZ NA ZEJŚCIE I FAZĘ DENNĄ (SOLO) ---
# Zanurzenie na dno (prędkość ok. 15 m/min)
czas_zanurzenia = glebokosc / 15
p_sr_zanurzenia = (p_powierzchnia + p_dno) / 2
gaz_norm_zanurzenie = czas_zanurzenia * sac_indywidualne * p_sr_zanurzenia

# Pobyt na dnie przez określony czas
gaz_norm_dno = czas_na_dnie * sac_indywidualne * p_dno

zuzycie_fazy_dennej_litry = gaz_norm_zanurzenie + gaz_norm_dno
zuzycie_fazy_dennej_bar = math.ceil(zuzycie_fazy_dennej_litry / pojemnosc_butli)

# Tyle realnie zostanie Ci w butli na dnie, zanim zaczniesz wracać
gaz_pozostaly_na_powrot_bar = cisnienie_startowe - zuzycie_fazy_dennej_bar


# --- KROK B: OBLICZAMY WYMAGANY ROCK BOTTOM NA WYJŚCIE AWARYJNE (DWIE OSOBY W STRESIE) ---
sac_awaryjne = sac_indywidualne * 2
gaz_faza_stres = 2 * sac_awaryjne * p_dno

if glebokosc > 6:
    dystans_faza1 = glebokosc - 6
    czas_faza1 = dystans_faza1 / 9
    p_sr_faza1 = (p_dno + p_przystanek) / 2
    gaz_faza_wynurzanie_glebokie = czas_faza1 * sac_awaryjne * p_sr_faza1
else:
    gaz_faza_wynurzanie_glebokie = 0

gaz_faza_przystanek = 3 * sac_awaryjne * p_przystanek
p_sr_faza2 = (p_przystanek + p_powierzchnia) / 2
gaz_faza_wynurzanie_plytkie = 2 * sac_awaryjne * p_sr_faza2

# Suma litrów powrotu awaryjnego + 15 bar technicznego zapasu na powierzchni
calkowity_gaz_awaryjny_litry = gaz_faza_stres + gaz_faza_wynurzanie_glebokie + gaz_faza_przystanek + gaz_faza_wynurzanie_plytkie
czysty_powrot_bar = calkowity_gaz_awaryjny_litry / pojemnosc_butli

# Ostateczny, wymagany dla tego profilu Rock Bottom (zaokrąglony do 10 bar)
rock_bottom_bar = math.ceil((czysty_powrot_bar + 15) / 10) * 10
rock_bottom_litry = rock_bottom_bar * pojemnosc_butli


# --- 🔘 KONSOLA STERUJĄCA SKI WAY ---
st.write("---")
st.markdown("### 🎛️ Parametry Wyjściowe (Konsola Ski Way):")

res_col1, res_col2 = st.columns(2)
with res_col1:
    st.metric(label="⏹️ WYMAGANY ROCK BOTTOM (Zapas na awarię)", value=f"{rock_bottom_bar} BAR", delta=f"{round(rock_bottom_litry)} litrów")
with res_col2:
    if gaz_pozostaly_na_powrot_bar > 0:
        st.metric(label="📉 CIŚNIENIE NA MANOMETRZE PO FAZIE DENNEJ", value=f"{gaz_pozostaly_na_powrot_bar} BAR", delta=f"Zużyłeś: {zuzycie_fazy_dennej_bar} bar")
    else:
        st.metric(label="📉 CIŚNIENIE NA MANOMETRZE PO FAZIE DENNEJ", value="0 BAR", delta="Gaz wyczerpany!")

# Dynamiczne, żołnierskie instrukcje bezpieczeństwa na bazie Twoich wyliczeń
if glebokosc > mod_metry:
    st.warning(f"⚠️ **OSTRZEŻENIE O ZAGROŻENIU (MOD):** Planowana głębokość ({glebokosc}m) przekracza maksymalną granicę operacyjną ({mod_metry:.1f} m) dla tej mieszanki! Pojawia się ryzyko toksyczności tlenowej.")

elif gaz_pozostaly_na_powrot_bar < rock_bottom_bar:
    st.warning(f"⚠️ **PLAN PODWYŻSZONEGO RYZYKA:** Po spędzeniu {czas_na_dnie} min na dnie zostanie Ci {gaz_pozostaly_na_powrot_bar} bar. To MNIEJ niż wymagany Rock Bottom ({rock_bottom_bar} bar)! W razie awarii partnerem zabraknie gazu. Skróć czas nurkowania!")

else:
    st.success(f"👉 **Wytyczne:** Wchodzisz z 200 bar. Po planowanym dopłynięciu i czasie na dnie, na manometrze powinno zostać Ci jeszcze **{gaz_pozostaly_na_powrot_bar} bar**. Ponieważ to więcej niż Twój Rock Bottom ({rock_bottom_bar} bar), nurkowanie jest w pełni zabezpieczone gazowo!")

if gestosc_na_dnie > 5.2 and glebokosc <= mod_metry:
    st.warning(f"⚠️ **Uwaga:** Gęstość gazu wynosi {gestosc_na_dnie:.1f} g/l. Spodziewaj się nieco większego oporu na automacie.")


# --- ANATOMIA PROCESÓW ---
st.write(" ")
with st.expander("🔍 Zobacz anatomię CAŁEGO nurkowania (Planowany profil):"):
    st.markdown(f"""
    Oto dokładna rozpiska, ile gazu zużyjesz podczas **całego, standardowego nurkowania** bez sytuacji awaryjnych (dla Twojego indywidualnego SAC = **{sac_indywidualne} l/min**):
    *   📉 **Zanurzenie na {glebokosc}m:** {round(gaz_norm_zanurzenie)} litrów *(Czas: {czas_zanurzenia:.1f} min)*
    *   ⏱️ **Pobyt na dnie ({czas_na_dnie} min):** {round(gaz_norm_dno)} litrów *(Zużycie stałe na maksymalnej głębokości)*
    *   *Uwaga: Normalne wynurzenie solo (gdyby nie było awarii) zużyłoby dodatkowo ok. {round((((glebokosc-6)/9) + 3 + 2) * sac_indywidualne * 2)} litrów.*
    """)

with st.expander("🔍 Zobacz szczegółową anatomię powrotu awaryjnego (Rock Bottom):"):
    st.markdown(f"""
    Oto dokładne wyliczenie rezerwy awaryjnej na wypadek awarii partnera na maksymalnej głębokości (łączny wydatek zespołu w stresie: **{sac_awaryjne} l/min**):
    *   **Faza 1 (Stres na dnie):** {round(gaz_faza_stres)} litrów *(2 minuty na opanowanie paniki)*
    *   **Faza 2 (Wynurzenie do 6m):** {round(gaz_faza_wynurzanie_glebokie)} litrów *(Prędkość bezpieczna 9 m/min)*
    *   **Faza 3 (Przystanek na 6m):** {round(gaz_faza_przystanek)} litrów *(3 minuty przystanku bezpieczeństwa)*
    *   **Faza 4 (Wynurzenie z 6m do powierzchni):** {round(gaz_faza_wynurzanie_plytkie)} litrów *(2 minuty bardzo powolnego kontrolowanego wynurzania)*
    *   🛡️ **Techniczna rezerwa końcowa:** {round(15 * pojemnosc_butli)} litrów *(Zawsze równe **15 barów**, gwarantujące swobodny oddech na powierzchni)*
    """)
