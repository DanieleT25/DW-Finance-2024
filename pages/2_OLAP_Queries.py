import streamlit as st
import pandas as pd
from utils.data_loader import load_data
from utils.charts_OLAP_Queries import topX, plot_transactions_by_quarter_type
from streamlit_theme import st_theme

clr = 'black'
theme = st_theme()
if theme is not None and theme.get("base") == "dark":
    clr = "white"


# Titolo della pagina
st.title("🔍 OLAP Queries")

# Carica i dati
df = load_data()

# --- QUERY 1 ---
st.header("1. Top 5 sectors by number of SELL transactions in China during 2024")

query1 = df[
    (df['TransactionType'] == 'SELL') &
    (df['country'] == 'China') &
    (df['year'] == 2024)
].groupby('sector').agg(
    numberOfTransactions=('numberOfTransactions', 'sum'),
    sumUnit=('sumUnit', 'sum')
).sort_values(by=['numberOfTransactions', 'sumUnit'], ascending=False).reset_index()

st.write("**OLAP operations:** Slice (`TransactionType = SELL`, `country = China`, `year = 2024`), Roll-up (`Quarter → Year`).")

meanNumberOfTransactions = query1['numberOfTransactions'].mean()
top5 = query1.head(5)

if len(query1) < 5:
    st.info(f"Only {len(query1)} sectors available for SELL transactions in China during 2024.")

st.dataframe(top5)
fig_query1 = topX(top5, meanNumberOfTransactions, clr)
st.plotly_chart(fig_query1, use_container_width=True)


# --- QUERY 2 ---
st.header("2. Top 5 industries by number of BUY transactions in Q4 of 2024")

query2 = df[
    (df['TransactionType'] == 'BUY') &
    (df['quarter'] == 'Q4') &
    (df['year'] == 2024)
].groupby('industry').agg(
    numberOfTransactions=('numberOfTransactions', 'sum'),
    sumUnit=('sumUnit', 'sum')
).sort_values(by='numberOfTransactions', ascending=False).reset_index()

st.write("**OLAP operations:** Slice (`TransactionType = BUY`, `quarter = Q4`, `year = 2024`)")

meanNumberOfTransactions = query2['numberOfTransactions'].mean()
top5 = query2.head(5)

if len(query2) < 5:
    st.info(f"Only {len(query2)} industries available for BUY transactions in Q4 of 2024.")

st.dataframe(top5)
fig_query2 = topX(top5, meanNumberOfTransactions, clr)
st.plotly_chart(fig_query2, use_container_width=True)

# --- QUERY 3 ---
st.header("3. Rank all quarters of 2024 by total number of transactions (BUY + SELL)")

query3 = df[
    (df['year'] == 2024) &
    (df['TransactionType'].isin(['BUY', 'SELL']))
].groupby(['quarter', 'TransactionType']).agg(
    numberOfTransactions=('numberOfTransactions', 'sum'),
    sumUnit=('sumUnit', 'sum')
).sort_values(by=['quarter', 'TransactionType'], ascending=True).reset_index()

pivot_df = query3.pivot(index='quarter', columns='TransactionType', values=['numberOfTransactions', 'sumUnit']).fillna(0)

st.write("**OLAP operations:** Slice (`year = 2024`, `TransactionType ∈ {BUY, SELL}`), Dice (`quarter × TransactionType`), Pivot (`TransactionType`, `sumUnit` as columns).")
st.dataframe(pivot_df)

fig_query3 = plot_transactions_by_quarter_type(pivot_df)
st.plotly_chart(fig_query3, use_container_width=True)
