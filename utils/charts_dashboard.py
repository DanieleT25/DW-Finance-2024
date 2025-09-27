import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import altair as alt

def topX(df, meanNumberOfTransactions, color, entity_type=None, df_original=None, sector_colors=None):
    nameColumn = df.columns[0]
    df_sorted = df.sort_values(by='numberOfTransactions', ascending=True).copy()
    
    # Hover text
    df_sorted['hover'] = 'Total Units: ' + df_sorted['sumUnit'].astype(int).astype(str)

    # Determina i colori delle barre
    bar_colors = []

    for _, row in df_sorted.iterrows():
        base_color = '#1f77b4'
        if entity_type == 'sector':
            base_color = sector_colors.get(row[nameColumn], '#1f77b4')

        elif entity_type == 'symbol' and df_original is not None:
            # Estrai symbol dalla label (cioè 'Company Name (SYMBOL)')
            if '(' in row[nameColumn]:
                symbol = row[nameColumn].split('(')[-1].replace(')', '').strip()
                temp_row = df_original[df_original['symbol'] == symbol]
                if not temp_row.empty:
                    sector = temp_row.iloc[0]['sector']
                    base_color = sector_colors.get(sector, '#1f77b4')

        elif entity_type == 'industry' and df_original is not None:
            lookup_val = row[nameColumn]
            temp_row = df_original[df_original[nameColumn] == lookup_val]
            if not temp_row.empty:
                sector = temp_row.iloc[0]['sector']
                base_color = sector_colors.get(sector, '#1f77b4')

        # Aggiungi trasparenza
        alpha = 1.0 if row['numberOfTransactions'] >= meanNumberOfTransactions else 0.3
        bar_colors.append(base_color.replace(')', f', {alpha})').replace('rgb', 'rgba'))

    # Plot
    fig = px.bar(
        df_sorted,
        y=nameColumn,
        x='numberOfTransactions',
        orientation='h',
        text='numberOfTransactions',
        hover_name='hover',
        labels={
            'numberOfTransactions': 'Number of Transactions',
            'sector': f'{nameColumn.capitalize()}',
        }
    )

    fig.update_traces(marker_color=bar_colors)
    fig.update_traces(hovertemplate='%{hovertext}<extra></extra>')

    fig.add_vline(
        x=meanNumberOfTransactions,
        line_dash="dash",
        line_color=color,
        annotation_text=f"Mean: {meanNumberOfTransactions:.0f}",
        annotation_position="top right",
        annotation_font_color=color,
        annotation_y=1.08
    )

    fig.update_layout(
        yaxis=dict(categoryorder='total ascending'),
        xaxis_visible=False,
        xaxis_showticklabels=False,
        showlegend=False,
        margin=dict(l=100, r=40, t=60, b=40),
        height=300
    )

    return fig


def plot_transactions(df):
    if df.empty:
        st.warning("No data available for the selected time range.")
        return

    # Ordina simboli per transazioni totali
    symbol_counts = (
        df.groupby('symbol')['n_total']
        .sum()
        .sort_values(ascending=False)
    )
    symbols = symbol_counts.index.tolist()

    # Multiselect
    selected_symbols = st.multiselect(
        "Choose symbol(s)",
        symbols,
        default=symbols[:3],
        key="symbol_multiselect_chart"
    )


    if not selected_symbols:
        st.warning("Please select at least one symbol.")
        return

    # Filtro per i simboli selezionati
    filtered = df[df['symbol'].isin(selected_symbols)]

    # Prepara il grafico
    chart = (
        alt.Chart(filtered)
        .mark_area(opacity=0.3)
        .encode(
            x=alt.X("quarter_label:N", title="Quarter", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("n_total:Q", title="Total Transactions", stack=None),
            color=alt.Color("symbol:N", title="Symbol"),
            tooltip=[
                alt.Tooltip("quarter_label:N", title="Quarter"),
                alt.Tooltip("symbol:N", title="Symbol"),
                alt.Tooltip("n_total:Q", title="Total Transactions"),
                alt.Tooltip("n_buy:Q", title="# BUY"),
                alt.Tooltip("n_sell:Q", title="# SELL")
            ]
        )
        .properties(height=250)
    )

    st.altair_chart(chart, use_container_width=True)






