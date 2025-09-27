import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import squarify

def adjust_alpha(hex_color, new_alpha='40'):
    # Esempio: "#4261A9F4" → "#4261A933"
    base = hex_color[:7]  # Prende #RRGGBB
    return base + new_alpha

def bestMetrics(df, metrics, symbolCompany):
    # Direzione desiderata per ogni metrica
    preference = {
        'net_profit_margin': 'higher',
        'roa': 'higher',
        'roe': 'higher',
        'profit_margins': 'higher',
        'pe_trailing': 'lower',
        'pe_forward': 'lower',
        'peg_ratio': 'lower',
        'price_to_sales': 'lower',
        'price_to_book': 'lower',
        'revenue_growth': 'higher',
        'earnings_growth': 'higher',
        'debt_to_equity': 'lower',
        'dividend_yield': 'higher',
        'payout_ratio': 'higher',
        'free_cashflow': 'higher'
    }

    # Calcolo dei percentili
    df_percentiles = df[metrics].copy()

    for col in df_percentiles.columns:
        metric = col[1]

        if metric == 'peg_ratio':
            # Escludi valori negativi o nulli
            valid_mask = df_percentiles[col] > 0
            ranks = df_percentiles.loc[valid_mask, col].rank(pct=True)
            df_percentiles[col] = ranks  # I valori non validi rimangono NaN
            if preference.get(metric, 'higher') == 'lower':
                df_percentiles[col] = 1 - df_percentiles[col]
        else:
            if preference.get(metric, 'higher') == 'higher':
                df_percentiles[col] = df_percentiles[col].rank(pct=True)
            else:
                df_percentiles[col] = 1 - df_percentiles[col].rank(pct=True)

    # Aggiungi simboli
    df_percentiles[('Info', 'symbol')] = df[('Info', 'symbol')]

    # Estrai percentili per la compagnia target
    atr_scores = df_percentiles[df_percentiles[('Info', 'symbol')] == symbolCompany].T
    atr_scores.columns = ['percentile_rank']

    # Seleziona la metrica migliore per ciascun gruppo
    best_metrics = {}
    for group in df_percentiles.columns.levels[0]:
        if group == 'Info':
            continue
        subset = atr_scores.loc[group]
        subset = subset.dropna()
        if not subset.empty:
            best_metric = subset['percentile_rank'].idxmax()
            best_metrics[group] = best_metric

    return best_metrics

def barplot_roa_by_area(ax, df, mtr, color, companySymbol, area, mtr_area, dim, low=True, horizontal=True, addCompany=True, ascending=False, meanLine=False, left=False, top=True, valueOut=False): 
    """
    Ai primi grafici mi accorsi che molto codice era ripetuto, quindi creai questa funzione per evitare di riscrivere lo stesso codice.
    Mai scelta fu così sbagliata, ma ormai era troppo tardi per tornare indietro.
    """
    company = df[df[('Info', 'symbol')] == companySymbol]
    area_value = company[('Info', area)].iloc[0]

    df_area = df[df[('Info', area)] == area_value]

    # Filtro speciale per payout_ratio
    if mtr == 'payout_ratio':
        df_area = df_area[(df_area[(mtr_area, mtr)] >= 0.3) & (df_area[(mtr_area, mtr)] <= 0.6)]

    df_area = df_area.sort_values(by=(mtr_area, mtr), ascending=not low)
    top5 = df_area.head(5)

    if addCompany and companySymbol not in top5[('Info', 'symbol')].values:
        top5 = pd.concat([top5, company], ignore_index=True)

    if mtr == 'payout_ratio':
        ax.set_title(f"Top 5 [30%-60%] in {area.title()} ({area_value})", fontsize=dim['title'], loc='left')
    else:
        ax.set_title(f"Top 5 in {area.title()} ({area_value})", fontsize=dim['title'], loc='left')
    ax.spines[:].set_visible(False)

    avg_area = df_area[(mtr_area, mtr)].mean()
    avg_text = f"{avg_area * 100:.2f}%" if mtr in ['roa', 'payout_ratio'] else f"{avg_area:.2f}"

    if horizontal:
        top5 = top5.sort_values(by=(mtr_area, mtr), ascending=low)
        clr = [color if sym == companySymbol else adjust_alpha(color) for sym in top5[('Info', 'symbol')]]
        labels = top5[('Info', 'company_name')].values
        values = top5[(mtr_area, mtr)].values

        bars = ax.barh(
            y=labels,
            width=values,
            height=0.6,
            color=clr
        )

        for bar, true_val in zip(bars, values):
            width = bar.get_width()
            y_pos = bar.get_y() + bar.get_height() / 2
            label = f"{true_val * 100:.2f}%" if mtr in ['roa', 'payout_ratio'] else f"{true_val:.2f}"

            if width >= 0:
                x_pos = width - (abs(width) * 0.02)
                ha = "right"
            else:
                x_pos = width + (abs(width) * 0.02)
                ha = "left"

            ax.text(x_pos, y_pos,
                    label, va="center", ha=ha,
                    fontsize=dim['text'], color='white', weight='bold')

        ax.tick_params(axis='y', labelsize=dim['ticks'])
        ax.xaxis.set_ticks([])

    else:
        if not ascending:
            top5 = top5.sort_values(by=(mtr_area, mtr), ascending=False)
            clr = [color if sym == companySymbol else adjust_alpha(color) for sym in top5[('Info', 'symbol')]]
            labels = top5[('Info', 'company_name')].values
            values = top5[(mtr_area, mtr)].values
        else:
            top5 = top5.sort_values(by=(mtr_area, mtr), ascending=low)
            clr = [color if sym == companySymbol else adjust_alpha(color) for sym in top5[('Info', 'symbol')]]
            labels = top5[('Info', 'company_name')].values
            values = top5[(mtr_area, mtr)].values

        bars = ax.bar(
            x=labels,
            height=values,
            width=0.6,
            color=clr
        )

        for bar, true_val in zip(bars, values):
            height = bar.get_height()
            x_pos = bar.get_x() + bar.get_width() / 2
            label = f"{true_val * 100:.2f}%" if mtr in ['roa', 'payout_ratio'] else f"{true_val:.2f}"

            if valueOut:
                y_pos = height + abs(height) * 0.02 if height >= 0 else height - abs(height) * 0.02
                va = "bottom" if height >= 0 else "top"
                colorValue = "black"
            else:
                y_pos = height - abs(height) * 0.02 if height >= 0 else height + abs(height) * 0.02
                va = "top" if height >= 0 else "bottom"
                colorValue = "white"

            ax.text(x_pos, y_pos, label, ha="center", va=va,
                    fontsize=dim['text'], color=colorValue, weight='bold')

        ax.tick_params(axis='x', labelsize=dim['ticks'], rotation=45)
        ax.yaxis.set_ticks([])


    if meanLine:
        if horizontal:
            ax.axvline(x=avg_area, color='gray', linestyle='--')
            ax.text(x=avg_area, y=-1, s=f"Average ({area}) \n {avg_text}", va="center", ha="center", color="gray", fontsize=dim['labels'])
        else:
            ax.axhline(y=avg_area, color='gray', linestyle='--')
            ax.text(y=avg_area, x=-1, s=f"Average ({area}) \n {avg_text}", va="center", ha="center", color="gray", fontsize=dim['labels'])
    else:
        ax.text(
            0.05 if left==True else 1.0, 0.1 if horizontal and not top else 0.95,
            f"Average ({area}): {avg_text}",
            transform=ax.transAxes,
            ha='left' if left==True else 'right', va='top',
            fontsize=dim['labels'], color='gray', style='italic'
        )

    if not addCompany:
        val = company[(mtr_area, mtr)].iloc[0]
        val_text = f"{val * 100:.2f}%" if mtr in ['roa', 'payout_ratio'] else f"{val:.2f}"
        ax.text(
            0.05 if left==True else 1.0, 0.2 if horizontal and not top else 0.85,
            f"{companySymbol}: {val_text}",
            transform=ax.transAxes,
            ha='left' if left==True else 'right', va='top',
            fontsize=dim['labels']*2, color=color, style='italic'
        )


def barplot_close_peers(ax, df, mtr, mtr_area, companySymbol, dim, color="#4261A9F4", ascending=True, orientation="horizontal"):
    """
    Funzione creata perché mi sono seccato a modificare la precedente
    """
    company = df[df[('Info', 'symbol')] == companySymbol]
    if company.empty:
        ax.text(0.5, 0.5, "Company not found", ha="center", va="center", fontsize=dim['text'])
        return

    company_mc = company[('Info', 'market_cap')].iloc[0]
    df_valid = df.dropna(subset=[(mtr_area, mtr)]).copy()
    df_valid['market_diff'] = abs(df_valid[('Info', 'market_cap')] - company_mc)

    # Seleziona i 5 più vicini (escludendo la company)
    top5 = df_valid[df_valid[('Info', 'symbol')] != companySymbol].nsmallest(5, 'market_diff')
    top5 = pd.concat([top5, company], ignore_index=True)

    # Ordina per metrica
    top5 = top5.sort_values(by=(mtr_area, mtr), ascending=ascending)

    # Dati da visualizzare
    clr = [color if sym == companySymbol else adjust_alpha(color) for sym in top5[('Info', 'symbol')]]
    labels = top5[('Info', 'company_name')].values
    values = top5[(mtr_area, mtr)].values

    ax.set_title("Top 5 Closest by Market Cap to ATR", fontsize=dim['title'], loc='left')
    ax.spines[:].set_visible(False)

    if orientation == "vertical":
        bars = ax.bar(x=labels, height=values, width=0.6, color=clr)
        for bar, val in zip(bars, values):
            x_pos = bar.get_x() + bar.get_width() / 2
            label = f"{val * 100:.2f}%" if mtr in ['roa', 'payout_ratio'] else f"{val:.2f}"
            label_margin = max(abs(val) * 0.01, 0.02)
            y_pos = val + label_margin if val >= 0 else val - label_margin

            if abs(val) > 0.1:
                va = 'bottom' if val >= 0 else 'top'
                text_color = 'black'
            else:
                va = 'bottom'
                text_color = 'white'
                y_pos = 0.02

            ax.text(x_pos, y_pos, label, ha='center', va=va,
                    fontsize=dim['text'], color=text_color, weight='bold')

        ax.axhline(y=0, color='gray', linewidth=1)
        ax.tick_params(axis='x', labelrotation=45, labelsize=dim['ticks'])
        ax.tick_params(axis='y', labelsize=dim['ticks'])
        ax.xaxis.set_ticks_position('none')

    else:
        bars = ax.barh(y=labels, width=values, height=0.6, color=clr)
        for bar, val in zip(bars, values):
            y_pos = bar.get_y() + bar.get_height() / 2
            label = f"{val * 100:.2f}%" if mtr in ['roa', 'payout_ratio'] else f"{val:.2f}"

            # Posizione *dentro* la barra
            label_margin = abs(val) * 0.02
            x_pos = val - label_margin if val > 0 else val + label_margin

            ha = 'right' if val > 0 else 'left'
            text_color = 'white'

            ax.text(x_pos, y_pos, label, va='center', ha=ha,
                    fontsize=dim['text'], color=text_color, weight='bold')

        ax.axvline(x=0, color='gray', linewidth=1)
        ax.tick_params(axis='y', labelsize=dim['ticks'])
        ax.xaxis.set_ticks_position('none')


def treemap_roa_by_area(ax, df, mtr, dim, mtr_area, color='#4261A9F4', company_symbol='ATR'):
    company = df[df[('Info', 'symbol')] == company_symbol]
    if company.empty:
        print(f"Azienda {company_symbol} non trovata.")
        return

    company_mc = company[('Info', 'market_cap')].iloc[0]

    df_valid = df.dropna(subset=[(mtr_area, mtr)]).copy()
    df_valid['market_diff'] = abs(df_valid[('Info', 'market_cap')] - company_mc)

    # Escludi metrica <= 0 (evita errore squarify)
    df_valid = df_valid[df_valid[(mtr_area, mtr)] > 0]

    df_closest = df_valid[df_valid[('Info', 'symbol')] != company_symbol].nsmallest(5, 'market_diff')

    if company[(mtr_area, mtr)].iloc[0] > 0:
        df_closest = pd.concat([df_closest, company], ignore_index=True)

    sizes = df_closest[(mtr_area, mtr)].values
    if (sizes <= 0).any() or len(sizes) == 0:
        ax.text(0.5, 0.5, "No valid data to plot", ha='center', va='center', fontsize=dim['text'])
        ax.axis('off')
        return

    labels = [
        (
            f"{row[('Info', 'symbol')]} "
            f"({row[(mtr_area, mtr)] * 100:.2f}%" if mtr in ['roa', 'payout_ratio']
            else f"{row[('Info', 'symbol')]} ({row[(mtr_area, mtr)]:.2f}"
        ) + f")\n{row[('Info', 'market_cap')] / 1e9:.2f}B"
        for _, row in df_closest.iterrows()
    ]
    colors = [color if sym == company_symbol else adjust_alpha(color) for sym in df_closest[('Info', 'symbol')]]

    squarify.plot(
        sizes=sizes,
        label=labels,
        color=colors,
        ax=ax,
        text_kwargs={'fontsize': dim['labels']},
        bar_kwargs={'edgecolor': 'white', 'linewidth': 2}
    )

    ax.set_title(f"Top 5 Closest by Market Cap to ATR (size: {mtr.replace("_", " ")})", loc='left', fontsize=dim['title'])
    ax.axis('off')

def scatter_plot(ax, df_comp, mtr_area1, metric1, mtr_area2, metric2, companySymbol='ATR'):
    company = df_comp[df_comp[('Info', 'symbol')] == companySymbol]
    if company.empty:
        ax.text(0.5, 0.5, "Company not found", ha="center", va="center")
        return

    val1 = company[(mtr_area1, metric1)].iloc[0]
    val2 = company[(mtr_area2, metric2)].iloc[0]
    sector_target = company[('Info', 'sector')].iloc[0]

    metric1_low_value = val1 * 0.75
    metric1_high_value = val1 * 1.25
    metric2_low_value = val2 * 0.75
    metric2_high_value = val2 * 1.25

    filtered_df = df_comp[
        (df_comp[(mtr_area1, metric1)] >= metric1_low_value) &
        (df_comp[(mtr_area1, metric1)] <= metric1_high_value) &
        (df_comp[(mtr_area2, metric2)] >= metric2_low_value) &
        (df_comp[(mtr_area2, metric2)] <= metric2_high_value)
    ]

    median_metric1 = filtered_df[(mtr_area1, metric1)].median()
    median_metric2 = filtered_df[(mtr_area2, metric2)].median()

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.axvline(x=median_metric1, color='gray', linestyle='--')
    ax.axhline(y=median_metric2, color='gray', linestyle='--')
    ax.scatter(median_metric1, median_metric2, color='gray', s=100)

    mask_above_median = (
        (filtered_df[(mtr_area1, metric1)] > median_metric1) &
        (filtered_df[(mtr_area2, metric2)] > median_metric2)
    )
    mask_selectedCompany = (filtered_df[('Info', 'symbol')] == companySymbol)
    mask_below_or_equal_median = ~mask_above_median

    ax.scatter(filtered_df[mask_below_or_equal_median][(mtr_area1, metric1)],
               filtered_df[mask_below_or_equal_median][(mtr_area2, metric2)],
               color=(169/255, 68/255, 66/255, 0.35), marker='x')

    scaling_factor = 1e8

    for idx, row in filtered_df[mask_above_median | mask_selectedCompany].iterrows():
        marker_size = row[('Info', 'market_cap')] / scaling_factor
        is_target = row[('Info', 'symbol')] == companySymbol
        is_same_sector = row[('Info', 'sector')] == sector_target

        color = (66/255, 103/255, 169/255, 1) if is_target else (169/255, 68/255, 66/255, 0.85)
        marker = 'o' if is_same_sector else '^'

        ax.scatter(
            row[(mtr_area1, metric1)],
            row[(mtr_area2, metric2)],
            color=color,
            s=marker_size,
            marker=marker,
            edgecolor='k' if is_target else 'none',
            linewidths=0.5
        )

        ax.annotate(row[('Info', 'symbol')], (row[(mtr_area1, metric1)], row[(mtr_area2, metric2)]),
                    textcoords="offset points", xytext=(10, -6), fontsize=14)

    ax.annotate("Median", xy=(median_metric1, median_metric2), xytext=(5, 5),
                textcoords="offset points", fontsize=15)

    ax.set_xlabel(metric1.replace("_", " ").title(), fontsize=20, loc='left')
    ax.set_ylabel(metric2.replace("_", " ").title(), fontsize=20, loc='bottom')

    ax.xaxis.get_offset_text().set_fontsize(14)
    ax.xaxis.get_offset_text().set_fontweight('bold')
    ax.yaxis.get_offset_text().set_fontsize(14)
    ax.yaxis.get_offset_text().set_fontweight('bold')

    legend_shapes = [
        plt.Line2D([], [], marker='o', linestyle='', color='gray', label='Same Sector'),
        plt.Line2D([], [], marker='^', linestyle='', color='gray', label='Other Sectors'),
    ]

    legend_sizes = [
        plt.Line2D([], [], marker='o', linestyle='', color='gray', markersize=np.sqrt(cap / scaling_factor), label=f'{label} Market Cap')
        for cap, label in zip([10e9, 5e9, 1e9], ['10B', '5B', '1B'])
    ]

    ax.legend(
        handles=legend_shapes + legend_sizes,
        loc='upper left',
        frameon=False,
        title="Shape = Sector | Size ∝ Market Cap",
        fontsize=14,
        title_fontsize=14,
        labelspacing=1.2
    )