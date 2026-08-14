import streamlit as st
import math

# Konfiguracja strony
st.set_page_config(page_title="Agent Rock Bottom", page_icon="🤿")

# Nagłówek aplikacji
st.title("🤿 Nurkowy Agent Rock Bottom")
st.write("Oblicz bezpieczną rezerwę gazu dla Ciebie i partnera.")

# Formularz wprowadzania danych
glebokosc = st.number_input("Głębokość nurkowania (metry):", min_value=1, max_value=50, value=30, step=1)
pojemnosc_butli = st.selectbox("Pojemność butli (litry):", [10, 12, 15, 18])
czas_nurkowania = st.number_input("Planowany czas na dnie (minuty):", min_value=1, max_value=90, value=15, step=1)

# Logika obliczeń (SAC 20 l/min, stres/dwie osoby = 40 l/min)
sac_awaryjne = 40
sac_indywidualne = 20

p_max = (glebokosc / 10) + 1
p_sr = (p_max + 1) / 2

# Faza awaryjna (2 min na dnie + wynurzenie + 3 min przystanek)
gaz_na_dnie = 2 * sac_awaryjne * p_max
gaz_wynurzanie = ((glebokosc / 10) + 3) * sac_awaryjne * p_sr
rock_bottom_litry = gaz_na_dnie + gaz_wynurzanie

# Zaokrąglenie Rock Bottom w barach w górę do pełnych 10 bar
rock_bottom_bar = math.ceil((rock_bottom_litry / pojemnosc_butli) / 10) * 10

# Faza planowana
gaz_planowany = czas_nurkowania * sac_indywidualne * p_max
wymagany_gaz_start = gaz_planowany + rock_bottom_litry
wymagane_cisnienie_start = math.ceil(wymagany_gaz_start / pojemnosc_butli)

# Wyświetlanie wyników
st.subheader("📊 Wyniki analizy bezpieczeństwa:")

st.error(f"🔴 ROCK BOTTOM: {rock_bottom_bar} bar")
st.caption("🚨 Gdy Twój manometr wskaże tę wartość, musicie natychmiast rozpocząć wynurzanie!")

st.success(f"🟢 Minimalne ciśnienie startowe: {wymagane_cisnienie_start} bar")

# Ostrzeżenie o przekroczeniu standardowego ciśnienia
if wymagane_cisnienie_start > 200:
    st.warning("⚠️ Uwaga: Ten plan wymaga więcej niż standardowe 200 bar w jednej butli! Skróć czas lub weź większą butlę.")
