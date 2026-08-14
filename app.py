import streamlit as st
import math

# 1. Konfiguracja aplikacji i nazwy w oknie przeglądarki
st.set_page_config(page_title="Ski Way Diving Machine", page_icon="🤿", layout="centered")

# Nagłówek aplikacji
st.title("🤿 Ski Way Diving Machine")
st.subheader("Kompletny planer profili nurkowych i rezerw gazowych")
st.write("---")

# --- SKRÓCONA DEFINICJA NA GÓRZE ---
st.markdown("""
### 🧠 Czym jest Rock Bottom?
**Rock Bottom (Żelazna Rezerwa)** to krytyczne ciśnienie w butli, przy którym należy natychmiast rozpocząć wspólne wynurzanie z partnerem oddychającym z Twojego zapasowego automatu w sytuacji awaryjnej.
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

    cisnienie_startowe = 200
    gestosc_na_dnie = 1.29 * ((glebokosc / 10) + 1)

with tab2:
    st.markdown("### Dostosuj parametry fizjologiczne")
    sac_indywidualne = st.slider("Twoje standardowe zużycie (SAC) [l/min]:", min_value=10, max_value=30, value=20, step=1)
    ppo2_custom = st.slider("Limit ciśnienia parcjalnego tlenu (PPO₂):", min_value=1.2, max_value=1.6, value=1.4, step=0.1)
    
    mod_metry = (ppo2_custom / fo2 - 1) * 10

# --- MATEMATYKA FIZYCZNA PROFILU NURKOWANIA ---
p_dno = (glebokosc / 10) + 1
p_przystanek = (6 / 10) + 1
p_powierzchnia = 1.0

# --- 1. OBLICZENIA DLA NORMALNEGO SCENARIUSZA (ZUŻYCIE INDYWIDUALNE) ---
# Zanurzenie: prędkość ok. 15 m/min. Średnie ciśnienie to średnia z powierzchni i dna.
czas_zanurzenia = glebokosc / 15
p_sr_zanurzenia = (p_powierzchnia + p_dno) / 2
gaz_norm_zanurzenie = czas_zanurzenia * sac_indywidualne * p_sr_zanurzenia

# Faza denna: planowany czas na dnie przy maksymalnym ciśnieniu
gaz_norm_dno = czas_na_dnie * sac_indywidualne * p_dno

# Wynurzenie normalne do 6m (prędkość 9 m/min)
if glebokosc > 6:
    czas_wyn_norm1 = (glebokosc - 6) / 9
    p_sr_wyn_norm1 = (p_dno + p_przystanek) / 2
    gaz_norm_wyn_glebokie = czas_wyn_norm1 * sac_indywidualne * p_sr_wyn_norm1
else:
    gaz_norm_wyn_glebokie = 0

# Przystanek bezpieczeństwa solo (3 min na 6m)
gaz_norm_przystanek = 3 * sac_indywidualne * p_przystanek

# Końcówka z 6m do powierzchni (2 min)
p_sr_wyn_norm2 = (p_przystanek + p_powierzchnia) / 2
gaz_norm_wyn_plytkie = 2 * sac_indywidualne * p_sr_wyn_norm2

# Suma planowanego normalnego zużycia gazu w litrach i barach
suma_normalne_litry = gaz_norm_zanurzenie + gaz_norm_dno + gaz_norm_wyn_glebokie + gaz_norm_przystanek + gaz_norm_wyn_plytkie
normalne_zuzycie_bar = math.ceil(suma_normalne_litry / pojemnosc_butli)


# --- 2. OBLICZENIA DLA SCENARIUSZA AWARYJNEGO (ROCK BOTTOM - DWIE OSOBY W STRESIE) ---
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

calkowity_gaz_litry = gaz_faza_stres + gaz_faza_wynurzanie_glebokie + gaz_faza_przystanek + gaz_faza_wynurzanie_plytkie
rock_bottom_bar = math.ceil((calkowity_gaz_litry / pojemnosc_butli) / 10) * 10


# --- KOŃCOWA WERYFIKACJA POJEMNOŚCI BALANSU GAZOWEGO ---
# Całkowity gaz potrzebny na zrealizowanie planu i zachowanie Rock Bottom
calkowity_wymagany_gaz_bar = normalne_zuzycie_bar + rock_bottom_bar
pozostale_cisnienie_wyjsciowe = cisnienie_startowe - normalne_zuzycie_bar

# --- WYŚWIETLANIE WYNIKÓW ---
st.write("---")
st.markdown("### 📊 Wynik Analizy Obciążeń Gazowych:")

res_col1, res_col2 = st.columns(2)
with res_col1:
    st.metric(label="🚨 ŻELAZNA REZERWA (ROCK BOTTOM)", value=f"{rock_bottom_bar} BAR")
with res_col2:
    st.metric(label="📉 PLANOWANE ZUŻYCIE GAZU (SOLO)", value=f"{normalne_zuzycie_bar} BAR")

# Komunikaty bezpieczeństwa i podsumowania taktyczne
if glebokosc > mod_metry:
    st.error(f"☠️ **KRYTYCZNE ZAGROŻENIE!** Planowana głębokość ({glebokosc}m) przekracza MOD ({mod_metry:.1f}m). Ryzyko toksyczności tlenowej!")
elif calkowity_wymagany_gaz_bar > cisnienie_startowe:
    st.error(f"🚨 **PLAN NIEBEZPIECZNY!** Łącznie na nurkowanie i rezerwę potrzebujesz {calkowity_wymagany_gaz_bar} bar. W butli 200 bar ZABRAKNIE GAZU! Skróć czas lub weź większą butlę.")
else:
    st.success(f"✅ Plan bezpieczny. Jeśli nurkowanie przebiegnie bezawaryjnie, wyjdziesz z wody mając na manometrze około **{pozostale_cisnienie_wyjsciowe} bar**.")

if gestosc_na_dnie > 5.2 and glebokosc <= mod_metry:
    st.warning(f"💨 **Gęstość gazu na dnie:** {gestosc_na_dnie:.1f} g/l. Oddychanie będzie stawiało większy opór.")


# --- NOWOŚĆ: ANATOMIA CAŁEGO PROCESU NURKOWANIA (NORMALNY PROFIL) ---
st.write(" ")
with st.expander("🔍 Zobacz anatomię CAŁEGO nurkowania (Planowany profil):"):
    st.markdown(f"""
    Oto dokładna rozpiska, ile gazu zużyjesz podczas **całego, standardowego nurkowania** bez sytuacji awaryjnych (dla Twojego indywidualnego SAC = **{sac_indywidualne} l/min**):
    *   📉 **Zanurzenie na {glebokosc}m:** {round(gaz_norm_zanurzenie)} litrów *(Czas: {czas_zanurzenia:.1f} min przy prędkości 15 m/min)*
    *   ⏱️ **Pobyt na dnie ({czas_na_dnie} min):** {round(gaz_norm_dno)} litrów *(Zużycie stałe na maksymalnej głębokości)*
    *   📈 **Wynurzenie do strefy przystanków (do 6m):** {round(gaz_norm_wyn_glebokie)} litrów *(Czas: {((glebokosc-6)/9):.1f} min przy prędkości 9 m/min)*
    *   🛑 **Przystanek bezpieczeństwa (3 min na 6m):** {round(gaz_norm_przystanek)} litrów
    *   ⛵ **Wynurzenie z 6m do powierzchni:** {round(gaz_norm_wyn_plytkie)} litrów *(Czas: 2 minuty bardzo wolnego wynurzania)*
    
    **Łącznie zużyjesz:** {round(suma_normalne_litry)} litrów gazu, co w Twojej butli przekłada się na około **{normalne_zuzycie_bar} bar**.
    """)


# --- POWRÓT DO STAREGO ROZSTAWU DETALI DETALI AWARYJNYCH ---
with st.expander("🔍 Zobacz szczegółową anatomię powrotu awaryjnego (Rock Bottom):"):
    st.markdown(f"""
    Oto dokładne wyliczenie rezerwy awaryjnej na wypadek awarii partnera na maksymalnej głębokości (łączny wydatek zespołu w stresie: **{sac_awaryjne} l/min**):
    *   **Faza 1 (Stres na dnie):** {round(gaz_faza_stres)} litrów *(Czas: 2 minuty na opanowanie paniki i podanie automatu)*
    *   **Faza 2 (Wynurzenie do 6m):** {round(gaz_faza_wynurzanie_glebokie)} litrów *(Czas wynurzania: {((glebokosc-6)/9):.1f} min przy prędkości 9 m/min)*
    *   **Faza 3 (Przystanek na 6m):** {round(gaz_faza_przystanek)} litrów *(Czas: 3 minuty przystanku bezpieczeństwa dla dwóch osób)*
    *   **Faza 4 (Wynurzenie z 6m do powierzchni):** {round(gaz_faza_wynurzanie_plytkie)} litrów *(Czas: 2 minuty bardzo powolnego kontrolowanego wynurzania)*
    
    **Razem objętość potrzebnego gazu awaryjnego:** {round(calkowity_gaz_litry)} litrów. 
    Dzieląc to przez Twoją butlę {pojemnosc_butli}L i zaokrąglając dla bezpieczeństwa w górę, otrzymujemy właśnie żelazne **{rock_bottom_bar} bar**.
    """)
