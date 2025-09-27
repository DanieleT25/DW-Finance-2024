import streamlit as st
from streamlit_theme import st_theme

clr = 'black'
theme = st_theme()
if theme is not None and theme.get("base") == "dark":
    clr = "white"


# Titolo della pagina
st.title("🖼️ Dashboard and Scatter Gallery of AptarGroup, Inc.")

st.image("./images/1_dashboard.png", caption="Retourn on assets")
st.image("./images/2_dashboard.png", caption="Price to sales")
st.image("./images/3_dashboard.png", caption="Revenue growth")
st.image("./images/4_dashboard.png", caption="Payout ratio")

st.image("./images/1_scatterPlot.png", caption="P/E forward vs ROE")
st.image("./images/2_scatterPlot.png", caption="Debt/Equity vs ROE")