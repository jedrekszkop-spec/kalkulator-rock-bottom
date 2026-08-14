import streamlit as st
import math

# 1. Konfiguracja aplikacji i nazwy w oknie przeglądarki
st.set_page_config(page_title="Ski Way Diving Machine", page_icon="🤿", layout="centered")

# Nagłówek aplikacji
st.title("🤿 Ski Way Diving Machine")
st.subheader("Kompletny planer profili nurkowych i limitów bezpieczeństwa")
st.write("---")

# --- SKRÓCONA DEFINICJA NA GÓRZE ---
st.markdown("""
### 🧠 Czym jest Rock Bottom?
**Rock Bottom (Żelazna Rezerwa)** to krytyczne ciśnienie w butli, przy którym należy natychmiast rozpocząć wspólne wynurzanie z partnerem. 
*Ski Way Diving Machine wylicza tę rezerwę, a następnie automatycznie wskazuje Ci, ile dokładnie minut możesz bezpiecznie spędzić na dnie, zanim Twój manometr dotknie tej granicy (startując z 200 bar).*
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
    st.markdown("### Krok 2: Głębokość Docelowa")
    
    # Teraz pytamy wyłącznie o głębokość (limit do 100m)
    glebokosc = st.number_input("Wpisz planowaną głębokość nurkowania (metry):", min_value=1, max_value=100, value=30, step=1)
    st.caption("*(Maksymalna głębokość możliwa do wybrania: 100 m)*")

    cisnienie_startowe = 200
    gestosc_na_dnie = 1.29 * ((glebokosc / 10) + 1)

with tab2:
    st.markdown("### Dostosuj parametry fizjologiczne")
    sac_indywidualne = st.slider("Twoje standardowe zużycie (SAC) [l/min]:", min_value=10, max_value=30, value=20, step=1)

# --- MATEMATYKA FIZYCZNA PROFILU NURKOWANIA ---
p_dno = (glebokosc / 10) + 1
p_przystanek = (6 / 10) + 1
p_powierzchnia = 1.0

# --- 1. OBLICZAMY WYMAGANY ROCK BOTTOM NA WYJŚCIE AWARYJNE (DWIE OSOBY W STRESIE) ---
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


# --- 2. NOWOŚĆ: AUTOMATYCZNE OBLICZANIE MAKSYMALNEGO CZASU BEZPIECZNEGO ---
# Gaz zużywany solo na samo zanurzenie na dno (prędkość ok. 15 m/min)
czas_zanurzenia = glebokosc / 15
p_sr_zanurzenia = (p_powierzchnia + p_dno) / 2
gaz_norm_zanurzenie_litry = czas_zanurzenia * sac_indywidualne * p_sr_zanurzenia

# Dostępny gaz na całą fazę denną (Wchodzisz z 200 bar, musisz wyjść z Rock Bottom)
gaz_dostepny_faza_denna_bar = cisnienie_startowe - rock_bottom_bar
gaz_dostepny_faza_denna_litry = gaz_dostepny_faza_denna_bar * pojemnosc_butli

# Odejmujemy litry na zanurzenie
gaz_czysty_na_dnie_litry = gaz_dostepny_faza_denna_litry - gaz_norm_zanurzenie_litry

# Ile litrów zużywasz w 1 minutę na tej głębokości (solo)
zuzycie_minutowe_na_dnie_litry = sac_indywidualne * p_dno

# Obliczenie czasu (jeśli butla jest zbyt mała na powrót, czas wyniesie 0)
if gaz_czysty_na_dnie_litry > 0 and gaz_dostepny_faza_denna_bar > 0:
    maks_bezpieczny_czas_min = math.floor(gaz_czysty_na_dnie_litry / zuzycie_minutowe_na_dnie_litry)
    # Zabezpieczenie przed ujemnymi lub absurdalnymi wynikami
    if maks_bezpieczny_czas_min < 0: maks_bezpieczny_czas_min = 0
else:
    maks_bezpieczny_czas_min = 0


# --- BAZA DANYCH NDL (Do porównania) ---
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


# --- 🔘 KONSOLA STERUJĄCA SKI WAY ---
st.write("---")
st.markdown("### 🎛️ Parametry Wyjściowe (Konsola Ski Way):")

res_col1, res_col2 = st.columns(2)
with res_col1:
    st.metric(label="⏹️ ŻELAZNA REZERWA (Rock Bottom)", value=f"{rock_bottom_bar} BAR", delta=f"{round(rock_bottom_litry)} litrów")
with res_col2:
    st.metric(label="⏱️ MAKSYMALNY BEZPIECZNY CZAS NA DNIE", value=f"{maks_bezpieczny_czas_min} MIN", delta=f"Gaz na dno: {max(0, gaz_dostepny_faza_denna_bar)} bar")

# Dynamiczne, żołnierskie instrukcje bezpieczeństwa
if glebokosc > mod_metry:
    st.warning(f"⚠️ **OSTRZEŻENIE O ZAGROŻENIU (MOD):** Planowana głębokość ({glebokosc}m) przekracza maksymalną granicę operacyjną ({mod_metry:.1f} m) dla tej mieszanki przy krytycznym $PPO_2 = 1.6$!")

elif gaz_dostepny_faza_denna_bar <= 0:
    st.warning(f"⚠️ **PLAN PODWYŻSZONEGO RYZYKA:** Wybrana butla jest ZA MAŁA na tę głębokość. Sam powrót awaryjny zużyje więcej niż 200 bar! Nie wolno Ci spędzić ani minuty na dnie!")

else:
    st.success(f"👉 **Wytyczne:** Startujesz z 200 bar. Możesz spędzić na dnie maksymalnie **{maks_bezpieczny_czas_min} minut**. Twój manometr spadnie wtedy do **{rock_bottom_bar} bar** – w tym momencie bezwzględnie kończysz nurkowanie i wracasz. Na powierzchni zostanie Ci przepisowe 15 barów.")

# Dodatkowe ostrzeżenie, gdy czas gazowy przekracza limit bezdekompresyjny NDL
if maks_bezpieczny_czas_min > lim_ndl and gaz_dostepny_faza_denna_bar > 0 and glebokosc <= mod_metry:
    st.warning(f"⚠️ **OSTRZEŻENIE NDL (DEKOMPRESJA):** Twój zapas gazu pozwala na {maks_bezpieczny_czas_min} min, ale limit bezdekompresyjny (NDL) dla {glebokosc}m to tylko **{lim_ndl} min**. Jeśli zostaniesz na dnie dłużej niż {lim_ndl} min, wejdziesz w dekompresję!")

if gestosc_na_dnie > 5.2 and glebokosc <= mod_metry:
    st.warning(f"⚠️ **Uwaga:** Gęstość gazu wynosi {gestosc_na_dnie:.1f} g/l. Spodziewaj się nieco większego oporu na automacie.")


# --- ANATOMIA PROCESÓW (ZAKŁADKI) ---
st.write(" ")
with st.expander("🔍 Zobacz anatomię CAŁEGO nurkowania (Planowany profil):"):
    st.markdown(f"""
    Oto dokładna rozpiska, ile gazu zużyjesz, jeśli wykorzystasz maksymalny bezpieczny czas (**{maks_bezpieczny_czas_min} min**) na dnie bez sytuacji awaryjnych (dla Twojego indywidualnego SAC = **{sac_indywidualne} l/min**):
    *   📉 **Zanurzenie na {glebokosc}m:** {round(gaz_norm_zanurzenie_litry)} litrów *(Czas: {czas_zanurzenia:.1f} min)*
    *   ⏱️ **Maksymalny pobyt na dnie ({maks_bezpieczny_czas_min} min):** {round(maks_bezpieczny_czas_min * zuzycie_minutowe_na_dnie_litry)} litrów
    *   *Gdy zakończysz fazę denną, na Twoim manometrze zostanie dokładnie żelazne **{rock_bottom_bar} bar**, chroniące Ciebie i partnera.*
    """)

with st.expander("🔍 Zobacz szczegółową anatomię powrotu awaryjnego (Rock Bottom):"):
    st.markdown(f"""
    Oto dokładne wyliczenie rezerwy awaryjnej na wypadek awarii partnera na maksymalnej głębokości (łączny wydatek zespołu w stresie: **{sac_awaryjne} l/min**):
    *   **Faza 1 (Stres na dnie):** {round(gaz_faza_stres)} litrów *(2 minuty na opanowanie paniki i podanie automata)*
    *   **Faza 2 (Wynurzenie do 6m):** {round(gaz_faza_wynurzanie_glebokie)} litrów *(Prędkość bezpieczna 9 m/min)*
    *   **Faza 3 (Przystanek na 6m):** {round(gaz_faza_przystanek)} litrów *(3 minuty przystanku bezpieczeństwa)*
    *   **Faza 4 (Wynurzenie z 6m do powierzchni):** {round(gaz_faza_wynurzanie_plytkie)} litrów *(2 minuty bardzo powolnego kontrolowanego wynurzania)*
    *   🛡️ **Techniczna rezerwa końcowa:** {round(15 * pojemnosc_butli)} litrów *(Zawsze równe **15 barów**, gwarantujące swobodny oddech na powierzchni)*
    """)

