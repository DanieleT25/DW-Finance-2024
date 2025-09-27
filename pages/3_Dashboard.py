import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_data
from utils.charts_dashboard import topX, plot_transactions
from streamlit_theme import st_theme

st.set_page_config(page_title="📊 Time Analysis Dashboard", layout="wide")

clr = 'black'
theme = st_theme()
if theme is not None and theme.get("base") == "dark":
    clr = "white"

# Caricamento dati
df = load_data()

# Genera label quarter per i filtri
df['quarter_label'] = df['quarter'] + ' - ' + df['year'].astype(str)
quarter_options = sorted(df['quarter_label'].unique(), key=lambda x: (int(x[-4:]), x[1]))

# Sidebar - filtro per quarter
st.sidebar.title("Filter by Quarter")
start_q = st.sidebar.selectbox("Start Quarter", quarter_options, index=0)
start_index = quarter_options.index(start_q)
end_q = st.sidebar.selectbox("End Quarter", quarter_options[start_index:], index=len(quarter_options[start_index:]) - 1)

# Sidebar - filtro per top
st.sidebar.title("The top x")
max_value = 10
top_x = st.sidebar.slider("x", min_value=1, max_value=max_value, value=5, step=1)

# Parsing start e end
start_quarter, start_year = start_q.split(' - ')
end_quarter, end_year = end_q.split(' - ')

# Filtro sui dati
filtered_df = df[
    ((df['year'] > int(start_year)) | ((df['year'] == int(start_year)) & (df['quarter'] >= start_quarter))) &
    ((df['year'] < int(end_year)) | ((df['year'] == int(end_year)) & (df['quarter'] <= end_quarter)))
]

# Top Settori
top_sectors = (
    filtered_df.groupby('sector').agg(
        numberOfTransactions=('numberOfTransactions', 'sum'),
        sumUnit=('sumUnit', 'sum')
    ).sort_values(by='numberOfTransactions', ascending=False).reset_index()
)

# Checkbox per modalità daltonica
colorblind_mode = st.sidebar.checkbox("Enable colorblind-friendly colors")

# Scegli la palette in base alla modalità
palette = px.colors.qualitative.Safe if colorblind_mode else px.colors.qualitative.Set2

# Mappa dinamica colori settore
sectors = top_sectors['sector'].unique().tolist()
sector_colors = {sector: palette[i % len(palette)] for i, sector in enumerate(sectors)}

# --- GRAFICI ---
# 1. Line chart - Transazioni nel tempo
summary = (
    filtered_df.groupby(['quarter_label', 'symbol', 'TransactionType'])
    .agg(numberOfTransactions=('numberOfTransactions', 'sum'))
    .reset_index()
)

pivot = summary.pivot_table(
    index=['quarter_label', 'symbol'],
    columns='TransactionType',
    values='numberOfTransactions',
    fill_value=0
).reset_index()

pivot = pivot.rename(columns={'BUY': 'n_buy', 'SELL': 'n_sell'})
pivot['n_total'] = pivot['n_buy'] + pivot['n_sell']

# 2. Bar chart - Top Symbols
top_symbol = (
    filtered_df.groupby(['company_name', 'symbol', 'sector']).agg(
        numberOfTransactions=('numberOfTransactions', 'sum'),
        sumUnit=('sumUnit', 'sum')
    ).sort_values(by='numberOfTransactions', ascending=False).reset_index()
)
top_symbol['label'] = top_symbol['company_name'] + ' (' + top_symbol['symbol'] + ')'


meanNumberOfTransactions = top_symbol['numberOfTransactions'].mean()
fig_top_symbols = topX(
    top_symbol[['label', 'numberOfTransactions', 'sumUnit', 'sector']].head(top_x),
    meanNumberOfTransactions,
    clr,
    entity_type="symbol",
    df_original=top_symbol,
    sector_colors=sector_colors
)

# 3. Bar chart - Top Sectors
meanNumberOfTransactions = top_sectors['numberOfTransactions'].mean()
fig_top_sectors = topX(
    top_sectors.head(top_x),
    meanNumberOfTransactions,
    clr,
    entity_type="sector",
    sector_colors=sector_colors
)

# 4. Bar chart - Top Industries
top_industries = (
    filtered_df.groupby(['industry', 'sector']).agg(
        numberOfTransactions=('numberOfTransactions', 'sum'),
        sumUnit=('sumUnit', 'sum')
    ).sort_values(by='numberOfTransactions', ascending=False).reset_index()
)

mean_industry = top_industries['numberOfTransactions'].mean()
fig_top_industries = topX(
    top_industries.head(top_x),
    mean_industry,
    clr,
    entity_type="industry",
    df_original=top_industries,
    sector_colors=sector_colors
)

# --- LAYOUT ---
st.title("📊 Time Analysis Dashboard")
st.markdown(f"##### Time range selected: **{start_q}** to **{end_q}**")

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Transactions over time")
        plot_transactions(pivot)
    with col2:
        st.subheader(f"Top {top_x} Symbols")
        st.plotly_chart(fig_top_symbols, use_container_width=True)

with st.container():
    col3, col4 = st.columns(2)
    with col3:
        st.subheader(f"Top {top_x} Sectors")
        if len(top_sectors) < top_x:
            st.info(f"Only {len(top_sectors)} sector available in the selected time range.")
        st.plotly_chart(fig_top_sectors, use_container_width=True)
    with col4:
        st.subheader(f"Top {top_x} Industries")
        st.plotly_chart(fig_top_industries, use_container_width=True)
