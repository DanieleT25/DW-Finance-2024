import plotly.express as px
import plotly.graph_objects as go


def topX(df, meanNumberOfTransactions, color):
    nameColumn = df.columns[0]
    df_sorted = df.sort_values(by='numberOfTransactions', ascending=True).copy()

    # Hover text
    df_sorted['hover'] = 'Total Units: ' + df_sorted['sumUnit'].astype(int).astype(str)

    # Colori dinamici in base alla media
    colors = [
        'rgba(31, 119, 180, 1.0)' if val >= meanNumberOfTransactions else 'rgba(31, 119, 180, 0.3)'
        for val in df_sorted['numberOfTransactions']
    ]

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

    # Imposta colori personalizzati
    fig.update_traces(marker_color=colors)

    # Hover semplificato
    fig.update_traces(
        hovertemplate='%{hovertext}<extra></extra>'
    )

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

def plot_transactions_by_quarter_type(pivot_df):
    quarter_order = ['Q4', 'Q3', 'Q2', 'Q1']
    pivot_df = pivot_df.reindex(quarter_order)

    pivot_df['total'] = pivot_df[('numberOfTransactions', 'BUY')] + pivot_df[('numberOfTransactions', 'SELL')]

    fig = go.Figure()

    # --- BUY ---
    fig.add_trace(go.Bar(
        y=pivot_df.index,
        x=pivot_df[('numberOfTransactions', 'BUY')],
        name='BUY',
        orientation='h',
        marker=dict(
            color='rgba(31, 119, 180, 0.7)',
            line=dict(color='rgba(31, 119, 180, 1.0)', width=2)
        ),
        hovertemplate='<b>BUY</b><br>Transactions: %{x}<br>Units: %{customdata}',
        customdata=pivot_df[('sumUnit', 'BUY')].astype(int),
        text=None  # No testo nella barra per BUY
    ))

    # --- SELL ---
    fig.add_trace(go.Bar(
        y=pivot_df.index,
        x=pivot_df[('numberOfTransactions', 'SELL')],
        name='SELL',
        orientation='h',
        marker=dict(
            color='rgba(255, 127, 14, 0.7)',
            line=dict(color='rgba(255, 127, 14, 1.0)', width=2)
        ),
        hovertemplate='<b>SELL</b><br>Transactions: %{x}<br>Units: %{customdata}',
        customdata=pivot_df[('sumUnit', 'SELL')].astype(int),
        text=pivot_df['total'].astype(int),
        textposition='outside',
            textfont=dict(
            size=14,
            color='white',
            family='Arial'
        )
    ))

    # Layout
    fig.update_layout(
        barmode='stack',
        title='Total Transactions per Quarter (2024)',
        xaxis_visible=False,
        xaxis_showticklabels=False,
        yaxis_title=None,
        yaxis=dict(categoryorder='array', categoryarray=quarter_order),
        template='simple_white',
        height=400,
        margin=dict(l=100, r=40, t=60, b=40),
        showlegend=True
    )

    return fig

