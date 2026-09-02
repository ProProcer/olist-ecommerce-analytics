import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pandas.tseries.offsets import DateOffset
import numpy as np
from pathlib import Path

st.set_page_config(page_title = 'Logistics Performance')
conn = st.connection('postgresql', type = 'sql')


freq_map = {
    'Monthly' : {'trunc' : 'month', 'period' : 'M', 'n_months' : 1},
    'Quarterly' : {'trunc' : 'quarter', 'period' : 'Q', 'n_months' : 3},
    'Yearly' : {'trunc' : 'year', 'period' : 'Y', 'n_months' : 12}
}

@st.cache_data(ttl = '5m')
def get_logistics_metrics(freq = 'Monthly'):

    params = freq_map[freq]


    query = f"""
        SELECT  
        DATE_TRUNC('{params['trunc']}', year_month) AS time_period,  
        SUM(on_time_orders) / SUM(total_orders) AS on_time_delivery_rate, 
        (SUM(handling_days * total_orders) / SUM(total_orders)) AS handling_days,
        (SUM(total_delivery_days * total_orders) / SUM(total_orders)) AS total_delivery_days,
        SUM(total_freight_value::NUMERIC) / NULLIF(SUM(total_freight_weight_kg), 0) AS freight_rate_by_weight,
        SUM(total_freight_value::NUMERIC) / NULLIF(SUM(total_freight_volume_m3), 0) AS freight_rate_by_volume,
        SUM(approved_count) AS approved_count,
        SUM(processing_count) AS processing_count,
        SUM(invoiced_count) AS invoiced_count,
        SUM(shipped_count) AS shipped_count,
        SUM(delivered_count) AS delivered_count,
        SUM(unavailable_count) AS unavailable_count,
        SUM(canceled_count) AS canceled_count
        FROM gold.monthly_logistics_metrics  
        GROUP BY DATE_TRUNC('{params['trunc']}', year_month)  
        ORDER BY time_period;
        """
    
    df = conn.query(query)
    df['time_period'] = df['time_period'].dt.to_period(params['period'])
    df.set_index('time_period', inplace = True)
    return df

@st.cache_data(ttl = '5m')
def get_fct_orders():
    query = f"""
        SELECT * FROM gold.fct_orders
    """
    df = conn.query(query)
    df['order_approved_at'] = pd.to_datetime(df['order_approved_at'])
    return df

@st.cache_data
def get_anomaly_scores():
    """Load the two final-model OOF exports and assign an order-level status."""
    project_root = Path(__file__).resolve().parent
    handling = pd.read_csv(
        project_root / 'data/processed/oof_predictions_handling_days.csv',
        usecols=['order_id', 'is_oof_scored', 'is_anomaly']
    ).rename(columns={
        'is_oof_scored': 'is_handling_scored',
        'is_anomaly': 'is_handling_anomaly'
    })
    transit = pd.read_csv(
        project_root / 'data/processed/oof_predictions_transit_days.csv',
        usecols=['order_id', 'is_oof_scored', 'is_anomaly']
    ).rename(columns={
        'is_oof_scored': 'is_transit_scored',
        'is_anomaly': 'is_transit_anomaly'
    })

    scores = handling.merge(transit, on='order_id', how='outer', validate='one_to_one')
    for column in ('is_handling_scored', 'is_transit_scored'):
        scores[column] = scores[column].astype('boolean').fillna(False).astype(bool)
    for column in ('is_handling_anomaly', 'is_transit_anomaly'):
        scores[column] = scores[column].astype('boolean')

    scores['is_oof_scored'] = (
        scores['is_handling_scored'] & scores['is_transit_scored']
    )
    scores['anomaly_category'] = pd.NA
    scored = scores['is_oof_scored']
    handling_anomaly = scores['is_handling_anomaly'].fillna(False)
    transit_anomaly = scores['is_transit_anomaly'].fillna(False)
    scores.loc[scored & ~handling_anomaly & ~transit_anomaly, 'anomaly_category'] = 'Fine'
    scores.loc[scored & handling_anomaly & ~transit_anomaly, 'anomaly_category'] = 'Handling anomaly'
    scores.loc[scored & ~handling_anomaly & transit_anomaly, 'anomaly_category'] = 'Carrier anomaly'
    scores.loc[scored & handling_anomaly & transit_anomaly, 'anomaly_category'] = 'Both anomalies'
    return scores[['order_id', 'is_oof_scored', 'anomaly_category']]

# On time delivery rate figure
def plot_otd_rate(df, time_period, sampling_freq):
    df['on_time_delivery_perc'] = df['on_time_delivery_rate'] * 100

    # categorize the current performance
    current_timestamp = df.loc[time_period, 'timestamp']
    if df.loc[time_period, 'on_time_delivery_rate'] > 0.95: #excellent case
        marker_line_color = 'rgba(28, 180, 27, 0.6)'
        font_color = 'green'
    elif df.loc[time_period, 'on_time_delivery_rate'] < 0.90: # bad case
        marker_line_color = 'rgba(255, 0, 0, 0.5)'
        font_color = 'red'
    else: #normal
        marker_line_color = '#000002'
        font_color = None
    
    otd_rate_fig = px.line( # base figure
        df, 
        x = 'timestamp', 
        y = 'on_time_delivery_perc',
        markers = True
    )
    otd_rate_fig.update_traces(
        opacity = 0.25
    )

    otd_rate_fig.update_layout(
        height = 270,
        showlegend = False,
        title_text = 'On Time Delivery (OTD) Rate'
    )

    n_months = freq_map[sampling_freq]['n_months']

    x_ticks = pd.to_datetime(np.concatenate( # prepare for changing xticks (cosmetic)
        (df.timestamp,
        df.timestamp.max() + DateOffset(months = n_months) * np.array([1, 2, 3]))
    ))

    otd_rate_fig.update_xaxes( # limit range and no panning
        range = (
            current_timestamp - DateOffset(months = n_months * 2, days = 1/3 * 30 * n_months), 
            current_timestamp + DateOffset(months = n_months * 2, days = 1/3 * 30 * n_months)
        ),
        tickvals = x_ticks,
        ticktext = x_ticks.to_period(freq_map[sampling_freq]['period']).astype('str'),
        fixedrange = True,
        title_text = None
    )

    otd_rate_fig.update_yaxes( # limit range and no panning
        range = (min(df.loc[time_period, 'on_time_delivery_perc'] - 1, 85), 100),
        fixedrange = True,
        title_text = None
    )
    
    otd_rate_fig.add_traces(
        (
        go.Scatter( # dot to emphasize on the current time
            x = [current_timestamp],
            y = [df.loc[time_period, 'on_time_delivery_perc']],
            marker_color = "#000001"
        ),
        go.Scatter( # outer ring on the dot to further emphasize
            x = [current_timestamp],
            y = [df.loc[time_period, 'on_time_delivery_perc']],
            marker_size = 16,
            marker_color = 'rgba(0, 0, 0, 0)',
            marker_line_width = 3,
            marker_line_color = marker_line_color
        )
        )
    )
    # excellent region
    otd_rate_fig.add_hrect(
        y0 = 95, y1 = 100, 
        fillcolor = 'green',
        opacity = 0.1, 
        layer = 'below',
        line_width = 0,
        annotation_text = 'Excellent',
        annotation_position = 'left bottom'
    )

    # bad region
    otd_rate_fig.add_hrect(
        y0 = 0, y1 = 90, 
        fillcolor = 'red',
        opacity = 0.1, 
        layer = 'below',
        line_width = 0,
        annotation_text = 'Underperforming',
        annotation_position = 'left top'
    )

    if ((time_period - 1 not in df.index) or
        (df.loc[time_period, 'on_time_delivery_rate'] ==  
        df.loc[time_period - 1, 'on_time_delivery_rate']) or
        np.isnan(df.loc[time_period, 'on_time_delivery_rate']) or
        np.isnan(df.loc[time_period - 1, 'on_time_delivery_rate'])):
        symbol = ''
    elif (df.loc[time_period, 'on_time_delivery_rate'] > 
        df.loc[time_period - 1, 'on_time_delivery_rate']):
        symbol = '▲'
    else:
        symbol = '▼'

    # the percentage
    otd_rate_fig.add_annotation(
        x = 0.95,
        y = 0.5,
        xref = 'paper',
        yref = 'paper',
        text = f'<b>{symbol} {df.loc[time_period, 'on_time_delivery_rate'] * 100:.1f}%</b>',
        font_size = 32,
        showarrow = False,
        font_color = font_color
    )
    
    return otd_rate_fig

def plot_delivery_time(fct_orders, is_split):
    delivery_time_fig = px.box(
        fct_orders, 
        x = 'total_delivery_days', 
        y = 'is_on_time' if is_split else None, 
        orientation = 'h'
    )
    delivery_time_fig.update_layout(
        title_text = 'Total Delivery Time',
        height = 270
    )
    delivery_time_fig.update_xaxes(
        fixedrange = True,
        title_text = "Duration (days)"
    )

    delivery_time_fig.update_yaxes(
        fixedrange = True,
        title_text = None
    )
    if is_split:
        delivery_time_fig.update_yaxes(
            tickvals = [0, 1],
            ticktext = ['Late', 'On Time']
        )

    return delivery_time_fig

def plot_stacked_bar(categories : dict, colors = None):
    if colors is None:
        colors = px.colors.qualitative.Safe

    assert len(categories) <= len(colors)

    bars = []
    legends = []
    for i, (cat, prop) in enumerate(categories.items()):
        bars.append(f'<div style="background-color: {colors[i]}; width: {prop * 100:.2f}%;"></div>')
        legends.append(f"""
            <div>
                <span style="width: 8pt; height: 8pt; display: 
                inline-block; background-color: {colors[i]}; border-radius: 20%;"></span> 
                <span style="font-size: 0.75rem;">{cat}</span>
            </div>
        """)
    html_code = f"""
    <style>
    .bar-container {{
        width: 100%;
        height: 0.5rem;
        display: flex;
        justify-content: space-between;
        border-radius: 10px;
        overflow: hidden;
    }}
    .legend-container{{
        width: 100%;
        display: flex;
        justify-content: space-around;
    }}
    </style>
    <div class="bar-container">{"".join(bars)}</div>
    <div class="legend-container">{"".join(legends)}</div>
    """
    st.html(html_code)


def show_delivery_time_composition(orders):
    """Show how the average delivery time is split between handling and transit."""
    handling_days = orders.handling_days.mean()
    transit_days = orders.transit_days.mean()
    total_delivery_days = orders.total_delivery_days.mean()

    if pd.isna(total_delivery_days) or total_delivery_days <= 0:
        st.info('Delivery-time composition is unavailable for this selection.')
        return

    st.markdown('###### Delivery Time Composition')
    plot_stacked_bar({
        f'Handling ({handling_days:.1f} days)': handling_days / total_delivery_days,
        f'Transit ({transit_days:.1f} days)': transit_days / total_delivery_days,
    })


def show_anomaly_proportions(orders):
    """Display mutually exclusive handling/transit anomaly categories."""
    categories = ('Fine', 'Handling anomaly', 'Carrier anomaly', 'Both anomalies')
    colors = ('#59A14F', '#F28E2B', '#4E79A7', '#B07AA1')
    scored_orders = orders[orders['is_oof_scored'].fillna(False)]

    st.markdown('###### Anomaly Proportion')
    if scored_orders.empty:
        st.info('No orders in this selection have OOF anomaly scores.')
        return

    proportions = scored_orders['anomaly_category'].value_counts(normalize=True)
    counts = scored_orders['anomaly_category'].value_counts()
    labels = {
        f'{category} ({counts.get(category, 0):,}; {proportions.get(category, 0):.1%})':
        proportions.get(category, 0)
        for category in categories
    }
    plot_stacked_bar(labels, colors=colors)
    st.caption(
        f'Based on {len(scored_orders):,} of {len(orders):,} orders with both OOF scores.'
    )


sampling_freq = st.selectbox(
    label = 'Select the Frequency',
    options = ('Monthly', 'Quarterly', 'Yearly')
)

df = get_logistics_metrics(sampling_freq)
df['timestamp'] = df.index.to_timestamp()

time_period = st.selectbox(
    label = 'Select Time Period',
    options = df.index.sort_values(ascending = False)
)


otd_rate_fig = plot_otd_rate(df, time_period, sampling_freq)
with st.container(border = True):
    st.write(otd_rate_fig)

fct_orders = get_fct_orders().merge(
    get_anomaly_scores(), on='order_id', how='left', validate='many_to_one'
)
fct_orders = fct_orders[
    fct_orders.order_approved_at.dt.to_period(freq_map[sampling_freq]['period']) == time_period
]



with st.container(border = True):
    st.toggle(
        "Split View",
        value = True,
        key="is_split_by_on_time",
        help="Toggle split by On Time vs. Late",
    )
    # Generate and display the figure below the header
    delivery_time_fig = plot_delivery_time(
        fct_orders, st.session_state.is_split_by_on_time
    )
    st.write(delivery_time_fig)

    if not st.session_state.is_split_by_on_time:
        show_delivery_time_composition(fct_orders)
        show_anomaly_proportions(fct_orders)
    else:
        for is_on_time, title in ((1, 'On-Time Delivery'), (0, 'Late Delivery')):
            orders = fct_orders[fct_orders.is_on_time == is_on_time]
            st.markdown(f'##### {title} ({len(orders):,} orders)')
            if orders.empty:
                st.info(f'No {title.lower()} orders are available for this selection.')
                continue
            show_delivery_time_composition(orders)
            show_anomaly_proportions(orders)

col1, col2 = st.columns(2)

with col1:
    
    with st.container(border = True):
        st.markdown("###### Freight Rate Efficiency")

        rate_by_weight_delta = (
            round(
                df.loc[time_period, 'freight_rate_by_weight'] - 
                df.loc[time_period - 1, 'freight_rate_by_weight'], 3
            )
            if time_period - 1 in df.index else 'Not available'
        )

        rate_by_volume_delta = (
            round(
                df.loc[time_period, 'freight_rate_by_volume'] - 
                df.loc[time_period - 1, 'freight_rate_by_volume'], 3
            )
            if time_period - 1 in df.index else 'Not available'
        )
        
        st.metric(
            label="Rate by Weight", 
            value=f"R$ {df.loc[time_period, 'freight_rate_by_weight']:.2f} / kg",
            delta= rate_by_weight_delta,
            delta_color = 'inverse'
        )
    
        st.metric(
            label="Rate by Volume", 
            value=f"R$ {df.loc[time_period, 'freight_rate_by_volume']:.2f} / m³",
            delta = rate_by_volume_delta,
            delta_color = 'inverse'
        )
with col2:
    with st.container(border = True):
        metrics_sr = df.loc[time_period]
        cols = pd.Series([
            "approved_count",
            "processing_count",
            "invoiced_count",
            "shipped_count",
            "delivered_count",
            "unavailable_count",
            "canceled_count"
        ])

        total_approved_orders = metrics_sr[cols].sum()
        delivery_counts_data = (
            df.loc[time_period, cols]
            .drop('delivered_count')
            .to_frame('count')
            .rename(index = pd.Series(cols.str[:-6].to_numpy(), index = cols))
            .reset_index(names = 'order_status')
        )

        fig = px.bar(
            data_frame = delivery_counts_data, 
            x = 'order_status',
            y = 'count',
            title = "Non-Delivered Order Breakdown"
        )
        fig.update_layout(
            height = 350,
            title_subtitle_text = f'Count: {int(total_approved_orders - metrics_sr.delivered_count)}/{int(total_approved_orders)}'
        )
        fig.update_xaxes(
            title_text = None
        )

        st.write(fig)
