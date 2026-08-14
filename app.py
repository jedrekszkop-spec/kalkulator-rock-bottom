import streamlit as st
import math

# Konfiguracja strony
st.set_page_config(page_title="Dokładny Agent Rock Bottom", page_icon="🤿", layout="centered")

st.title("🤿 W 100% Dokładny Agent Rock Bottom")
st.write("Profesjonalny kalkulator rezerwy gazu rozbity na 4 fazy awaryjne (dla Ciebie i partnera).")

# Formularz wprowadzania danych
glebokosc = st.number_input("Głębokość nurkowania (metry):", min_value=1, max_value=50, value=30, step=1)
pojemnosc_butli = st.selectbox("Pojemność Twojej butli (litry):", [10, 12, 15, 18])

# Założenie: Startujemy zawsze z 200 bar
cisnienie_startowe = 200
st.info(f"ℹ️ Kalkulator przyjmuje standardowe ciśnienie początkowe w butli: **{cisnienie_startowe} bar**.")

# --- DOKŁADNE OBLICZENIA LOGISTYKI AWARYJNEJ (SAC łączny w stresie = 40 l/min) ---
sac_awaryjne = 40

# 1. Ciśnienia w punktach kluczowych
p_dno = (glebokosc / 10) + 1
p_przystanek = (6 / 10) + 1  # Przystanek na 6 metrach = 1.6 ATA
p_powierzchnia = 1.0

# 2. Obliczenia fazowe (LITRY)
# Faza 1: Stres na dnie (2 minuty)
gaz_faza_stres = 2 * sac_awaryjne * p_dno

# Faza 2: Wynurzenie z dna do 6m (prędkość 9 m/min)
if glebokosc > 6:
    dystans_faza1 = glebokosc - 6
    czas_faza1 = dystans_faza1 / 9
    p_sr_faza1 = (p_dno + p_przystanek) / 2
    gaz_faza_wynurzanie_glebokie = czas_faza1 * sac_awaryjne * p_sr_faza1
else:
    gaz_faza_wynurzanie_glebokie = 0

# Faza 3: Przystanek bezpieczeństwa na 6m (3 minuty)
gaz_faza_przystanek = 3 * sac_awaryjne * p_przystanek

# Faza 4: Wynurzenie z 6m do powierzchni (bardzo powolne - 3 m/min, czyli 2 minuty)
czas_faza2 = 6 / 3
p_sr_faza2 = (p_przystanek + p_powierzchnia) / 2
gaz_faza_wynurzanie_plytkie = czas_faza2 * sac_awaryjne * p_sr_faza2

# Suma litrów
calkowity_gaz_litry = gaz_faza_stres + gaz_faza_wynurzanie_glebokie + gaz_faza_przystanek + gaz_faza_wynurzanie_plytkie

# Zamiana na bary i zaokrąglenie w górę do pełnych 10 bar
rock_bottom_bar = math.ceil((calkowity_gaz_litry / pojemnosc_butli) / 10) * 10

# Obliczanie dostępnego gazu dennego z butli 200 bar
dostepny_gaz_bar = cisnienie_startowe - rock_bottom_bar

# --- WYŚWIETLANIE WYNIKÓW ---
st.subheader("📊 Wyniki Analizy Bezpieczeństwa:")

st.error(f"🔴 TWÓJ ROCK BOTTOM: {rock_bottom_bar} bar")
st.caption(f"🚨 Gdy manometr pokaże {rock_bottom_bar} bar, musicie natychmiast obaj zacząć płynąć w górę!")

if dostepny_gaz_bar > 0:
    st.success(f"🟢 Gaz na fazę denną: {dostepny_gaz_bar} bar")
    st.write(f"Wchodząc do wody z ciśnieniem 200 bar, możesz zużyć maksymalnie **{dostepny_gaz_bar} bar** na dnie.")
else:
    st.warning("⚠️ NIEBEZPIECZNY PLAN! Sam Rock Bottom wymaga więcej gazu niż mieści butla 200 bar! Zmień butlę na większą lub zmniejsz głębokość.")

# Sekcja szczegółowa dla dociekliwych
with st.expander("🔍 Zobacz dokładny podział litrów gazu na etapy:"):
    st.write(f"*   **Rozwiązanie problemu na dnie (2 min):** {round(gaz_faza_stres)} litrów")
    st.write(f"*   **Wynurzenie na 6 metrów:** {round(gaz_faza_wynurzanie_glebokie)} litrów")
    st.write(f"*   **Przystanek bezpieczeństwa (3 min na 6m):** {round(gaz_faza_przystanek)} litrów")
    st.write(f"*   **Wynurzenie z 6m do powierzchni (2 min):** {round(gaz_faza_wynurzanie_plytkie)} litrów")
    st.write(f"**Łącznie potrzebujesz:** {round(calkowity_gaz_litry)} litrów awaryjnego gazu.")
