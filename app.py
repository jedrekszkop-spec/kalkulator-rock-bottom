import streamlit as st
import math

# Nagłówek aplikacji
st.title("🤿 Ski Way Diving Machine (Wersja Podstawowa)")
st.subheader("Prosty kalkulator Rock Bottom i planowania nurkowania")
st.write("---")

# 1. PARAMETRY WEJŚCIOWE
st.markdown("### 1. Wprowadź dane nurkowania:")

glebokosc = st.number_input("Głębokość nurkowania (metry):", min_value=1, max_value=100, value=30, step=1)
pojemnosc_butli = st.number_input("Pojemność butli (litry):", min_value=5, max_value=50, value=15, step=1)
czas_nurkowania = st.number_input("Planowany czas na dnie (minuty):", min_value=1, max_value=60, value=15, step=1)

sac_indywidualne = 20
sac_awaryjne = 40 

# 2. OBLICZENIA
p_max = (glebokosc / 10) + 1
p_sr = (p_max + 1) / 2

rock_bottom_litry = (2 * sac_awaryjne * p_max) + (((glebokosc / 10) + 3 + 2) * sac_awaryjne * p_sr)
rock_bottom_bar = math.ceil((rock_bottom_litry / pojemnosc_butli) / 10) * 10

gaz_planowany_litry = czas_nurkowania * sac_indywidualne * p_max
wymagany_gaz_start_litry = gaz_planowany_litry + rock_bottom_litry
wymagane_cisnienie_start = math.ceil(wymagany_gaz_start_litry / pojemnosc_butli)

# 3. WYNIKI
st.write("---")
st.markdown("### 📊 Wyniki analizy bezpieczeństwa:")

st.error(f"🔴 ROCK BOTTOM: {rock_bottom_bar} bar")
st.caption("🚨 Gdy Twój manometr wskaże tę wartość, musicie natychmiast rozpocząć wynurzanie!")

st.success(f"🟢 Minimalne ciśnienie startowe: {wymagane_cisnienie_start} bar")

if wymagane_cisnienie_start > 200:
    st.warning("⚠️ Uwaga: Ten plan wymaga więcej niż standardowe 200 bar w jednej butli!")
