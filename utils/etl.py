import pandas as pd

transaction = pd.read_csv('./data/raw_data/account-statement-1-1-2024-12-31-2024.csv', sep=';')
company = pd.read_csv('./data/raw_data/symbols.csv', sep=';')

transaction = transaction.drop(columns=["Unnamed: 5"])
transaction = transaction.dropna()

transaction['Date'] = pd.to_datetime(transaction['Date'], format='%d/%m/%Y %H:%M:%S')
transaction['quarter'] = 'Q' + transaction['Date'].dt.quarter.astype(str)
transaction['year'] = transaction['Date'].dt.year

dim_time = transaction[['Date']].drop_duplicates().copy()
dim_time['quarter'] = 'Q' + dim_time['Date'].dt.quarter.astype(str)
dim_time['year'] = dim_time['Date'].dt.year
dim_time = dim_time[['quarter', 'year']].drop_duplicates().sort_values(by=['year', 'quarter']).reset_index(drop=True)
dim_time['idTime'] = dim_time.index + 1
dim_time = dim_time[['idTime', 'quarter', 'year']]

dim_geography = company[['country']].drop_duplicates().copy()
dim_geography = dim_geography.sort_values('country').reset_index(drop=True)
dim_geography['idGeography'] = dim_geography.index + 1
dim_geography = dim_geography[['idGeography', 'country']]

dim_symbol = company[['symbol', 'company_name', 'sector', 'industry']].drop_duplicates().copy()
dim_symbol = dim_symbol.sort_values('symbol').reset_index(drop=True)
dim_symbol['idSymbol'] = dim_symbol.index + 1
dim_symbol = dim_symbol[['idSymbol', 'symbol', 'company_name', 'industry', 'sector']]

dim_transaction_type = transaction[['TransactionType']].drop_duplicates().copy()
dim_transaction_type = dim_transaction_type.sort_values('TransactionType').reset_index(drop=True)
dim_transaction_type['idTransactionType'] = dim_transaction_type.index + 1
dim_transaction_type = dim_transaction_type[['idTransactionType', 'TransactionType']]

transaction = transaction.merge(company[['symbol', 'country']], left_on='Symbol', right_on='symbol', how='left')
transaction = transaction.merge(dim_symbol[['idSymbol', 'symbol']], left_on='Symbol', right_on='symbol', how='left')
transaction = transaction.merge(dim_transaction_type, on='TransactionType', how='left')
transaction = transaction.merge(dim_geography[['idGeography', 'country']], on='country', how='left')
transaction = transaction.merge(dim_time, on=['quarter', 'year'], how='left')

fact_transaction = transaction.groupby(
    ['idTime', 'idSymbol', 'idTransactionType', 'idGeography']
).agg(
    numberOfTransactions=('IDTransaction', 'count'),
    sumUnit=('Unit', 'sum')
).reset_index()

dim_time.to_csv('./data/star_schema/dim_time.csv', index=False)
dim_geography.to_csv('./data/star_schema/dim_geography.csv', index=False)
dim_symbol.to_csv('./data/star_schema/dim_symbol.csv', index=False)
dim_transaction_type.to_csv('./data/star_schema/dim_transaction_type.csv', index=False)
fact_transaction.to_csv('./data/star_schema/fact_transaction.csv', index=False)
