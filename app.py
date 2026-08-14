import streamlit as st
import math

# 1. Konfiguracja aplikacji i nazwy w oknie przeglądarki
st.set_page_config(page_title="Ski Way Diving Machine", page_icon="🤿", layout="centered")

# Nagłówek aplikacji
st.title("🤿 Ski Way Diving Machine")
st.subheader("Profesjonalny kalkulator żelaznej rezerwy gazowej")
st.write("---")

# --- NOWOŚĆ: SEKCJA EDUKACYJNA NA GÓRZE STRONY ---
st.markdown("""
### 🧠 Czym jest Rock Bottom?
**Rock Bottom** (Żelazna Rezerwa) to minimalne ciśnienie w butli, przy którym **musisz bezwzględnie rozpocząć wynurzanie**. 
Jest to ilość gazu obliczona na wypadek **najczarniejszego scenariusza**: Twój partner traci cały gaz na maksymalnej głębokości, przechodzi na Twój zapasowy automat i w stanie dużego stresu (podwyższone zużycie gazu) bezpiecznie, wspólnie wynurzacie się na powierzchnię, wykonując po drodze przystanek bezpieczeństwa. 

*Pamiętaj: Rock Bottom nie jest gazem na wydłużenie nurkowania – to Twoja polisa na życie!*
""")
st.write("---")

# Podział na zakładki (Krok 1 i Zaawansowane zostają bez zmian)
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
    st.markdown("### Krok 2: Głębokość docelowa")
    
    # Teraz pytamy tylko o głębokość - czysto i przejrzyście
    glebokosc = st.number_input("Wpisz planowaną głębokość nurkowania (metry):", min_value=1, max_value=50, value=30, step=1)

    cisnienie_startowe = 200
    gestosc_na_dnie = 1.29 * ((glebokosc / 10) + 1)

with tab2:
    st.markdown("### Dostosuj parametry fizjologiczne")
    sac_indywidualne = st.slider("Twoje standardowe zużycie (SAC) [l/min]:", min_value=10, max_value=30, value=20, step=1)
    ppo2_custom = st.slider("Limit ciśnienia parcjalnego tlenu (PPO₂):", min_value=1.2, max_value=1.6, value=1.4, step=0.1)
    
    mod_metry = (ppo2_custom / fo2 - 1) * 10

# --- SILNIK OBLICZENIOWY ROCK BOTTOM (Dla dwóch osób w stresie) ---
sac_awaryjne = sac_indywidualne * 2
p_dno = (glebokosc / 10) + 1
p_przystanek = (6 / 10) + 1
p_powierzchnia = 1.0

# 1. Stres na dnie (2 minuty)
gaz_faza_stres = 2 * sac_awaryjne * p_dno

# 2. Wynurzenie z dna do strefy przystanków na 6m (prędkość 9 m/min)
if glebokosc > 6:
    dystans_faza1 = glebokosc - 6
    czas_faza1 = dystans_faza1 / 9
    p_sr_faza1 = (p_dno + p_przystanek) / 2
    gaz_faza_wynurzanie_glebokie = czas_faza1 * sac_awaryjne * p_sr_faza1
else:
    gaz_faza_wynurzanie_glebokie = 0

# 3. Przystanek bezpieczeństwa na 6m (standardowe 3 minuty)
gaz_faza_przystanek = 3 * sac_awaryjne * p_przystanek

# 4. Wolne wynurzenie z 6m na powierzchnię (prędkość 3 m/min = 2 minuty)
czas_faza2 = 6 / 3
p_sr_faza2 = (p_przystanek + p_powierzchnia) / 2
gaz_faza_wynurzanie_plytkie = czas_faza2 * sac_awaryjne * p_sr_faza2

# Suma litrów rezerwowych i przeliczenie na Bary (zaokrąglenie w górę do pełnych 10 bar)
calkowity_gaz_litry = gaz_faza_stres + gaz_faza_wynurzanie_glebokie + gaz_faza_przystanek + gaz_faza_wynurzanie_plytkie
rock_bottom_bar = math.ceil((calkowity_gaz_litry / pojemnosc_butli) / 10) * 10
dostepny_gaz_bar = cisnienie_startowe - rock_bottom_bar

# --- WYŚWIETLANIE WYNIKÓW (Proste i Przejrzyste) ---
st.write("---")
st.markdown("### 📊 Wynik Analizy Obciążeń Gazowych:")

res_col1, res_col2 = st.columns(2)
with res_col1:
    st.metric(label="🚨 ŻELAZNA REZERWA (ROCK BOTTOM)", value=f"{rock_bottom_bar} BAR")
with res_col2:
    if dostepny_gaz_bar > 0:
        st.metric(label="🟢 GAZ DOSTĘPNY NA FAZĘ DENNĄ", value=f"{dostepny_gaz_bar} BAR")
    else:
        st.metric(label="❌ GAZ DOSTĘPNY NA FAZĘ DENNĄ", value="BRAK")

# Alerty bezpieczeństwa pod spodem wyników
if glebokosc > mod_metry:
    st.error(f"☠️ **KRYTYCZNE ZAGROŻENIE!** Planowana głębokość ({glebokosc}m) przekracza MOD ({mod_metry:.1f}m) dla Twojego gazu! Ryzyko toksyczności tlenowej!")
elif dostepny_gaz_bar <= 0:
    st.error(f"🚨 **PLAN NIEBEZPIECZNY!** Wybrana butla ({pojemnosc_butli}L) jest za mała. Sam powrót awaryjny z głębokości {glebokosc}m wymaga więcej gazu niż mieści butla 200 bar!")
else:
    st.success(f"✅ Wchodząc do wody z butlą napełnioną do 200 bar, możesz zużyć maksymalnie **{dostepny_gaz_bar} bar**. Gdy manometr pokaże **{rock_bottom_bar} bar**, musicie natychmiast wracać!")

if gestosc_na_dnie > 5.2 and glebokosc <= mod_metry:
    st.warning(f"💨 **Gęstość gazu na dnie:** {gestosc_na_dnie:.1f} g/l (Norma bezpieczeństwa to 5.2). Pamiętaj, że oddychanie na tej głębokości będzie stawiało większy opór.")

# --- SEKCJA CIEKAWOSTKI (ANATOMIA POWROTU) ---
st.write(" ")
with st.expander("🔍 Zobacz szczegółową anatomię powrotu awaryjnego (Ciekawostka):"):
    st.markdown(f"""
    Oto dokładne wyliczenie, ile litrów gazu ucieka z Twojej butli sekunda po sekundzie, gdy oddychasz razem z partnerem w stresie (łączny wydatek zespołu: **{sac_awaryjne} l/min**):
    *   **Faza 1 (Stres na dnie):** {round(gaz_faza_stres)} litrów *(Czas: 2 minuty na opanowanie paniki i podanie automatu na głębokości {glebokosc}m)*
    *   **Faza 2 (Wynurzenie do 6m):** {round(gaz_faza_wynurzanie_glebokie)} litrów *(Czas wynurzania: {((glebokosc-6)/9):.1f} min z prędkością bezpieczną 9 m/min)*
    *   **Faza 3 (Przystanek na 6m):** {round(gaz_faza_przystanek)} litrów *(Czas: 3 minuty na rekreacyjny przystanek bezpieczeństwa)*
    *   **Faza 4 (Wynurzenie z 6m do powierzchni):** {round(gaz_faza_wynurzanie_plytkie)} litrów *(Czas: 2 minuty bardzo powolnego kontrolowanego wynurzania)*
    
    **Razem objętość potrzebnego gazu:** {round(calkowity_gaz_litry)} litrów. 
    Dzieląc to przez Twoją butlę {pojemnosc_butli}L i zaokrąglając dla bezpieczeństwa w górę, otrzymujemy właśnie równe **{rock_bottom_bar} bar**.
    """)
