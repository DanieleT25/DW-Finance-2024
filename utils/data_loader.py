import pandas as pd
import streamlit as st
import os


@st.cache_data
def load_data():
    if not os.path.exists('./data/star_schema/fact_transaction.csv'): import utils.etl

    dim_time = pd.read_csv('./data/star_schema/dim_time.csv')
    dim_geography = pd.read_csv('./data/star_schema/dim_geography.csv')
    dim_symbol = pd.read_csv('./data/star_schema/dim_symbol.csv')
    dim_transaction_type = pd.read_csv('./data/star_schema/dim_transaction_type.csv')
    fact_transaction = pd.read_csv('./data/star_schema/fact_transaction.csv')

    df = fact_transaction.merge(dim_time, on='idTime').merge(dim_symbol, on='idSymbol').merge(dim_geography, on='idGeography').merge(dim_transaction_type, on='idTransactionType')

    return df

