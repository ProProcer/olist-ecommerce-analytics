import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pandas.tseries.offsets import DateOffset
import numpy as np

st.set_page_config(page_title = 'Logistics Performance')
conn = st.connection('postgresql', type = 'sql')

st.cache_data(ttl = '5m')

freq_map = {
    'Monthly' : {'trunc' : 'month', 'period' : 'M', 'n_months' : 1},
    'Quarterly' : {'trunc' : 'quarter', 'period' : 'Q', 'n_months' : 3},
    'Yearly' : {'trunc' : 'year', 'period' : 'Y', 'n_months' : 12}
}
def get_logistics_metrics(freq = 'monthly'):

    params = freq_map[freq]


    query = f"""
        SELECT  
        DATE_TRUNC('{params['trunc']}', year_month) AS time_period,  
        SUM(on_time_orders) / SUM(total_orders) AS on_time_delivery_rate, 
        (SUM(handling_days * total_orders) / SUM(total_orders)) AS handling_days,
        (SUM(total_delivery_days * total_orders) / SUM(total_orders)) AS total_delivery_days
        FROM gold.monthly_logistics_metrics  
        GROUP BY DATE_TRUNC('{params['trunc']}', year_month)  
        ORDER BY time_period;
        """
    
    df = conn.query(query)
    df['time_period'] = df['time_period'].dt.to_period(params['period'])
    df.set_index('time_period', inplace = True)
    return df

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

def get_fct_orders():
    query = f"""
        SELECT * FROM gold.fct_orders
    """
    df = conn.query(query)
    return df

# On time delivery rate figure
def plot_otd_rate(df):
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

    x_ticks = pd.Series(np.concatenate( # prepare for changing xticks (cosmetic)
        (df.timestamp,
        df.timestamp.max() + DateOffset(months = n_months) * np.array([1, 2, 3]))
    ))

    otd_rate_fig.update_xaxes( # limit range and no panning
        range = (
            current_timestamp - DateOffset(months = n_months * 2, days = 1/3 * 30 * n_months), 
            current_timestamp + DateOffset(months = n_months * 2, days = 1/3 * 30 * n_months)
        ),
        tickvals = x_ticks,
        ticktext = x_ticks.dt.to_period(freq_map[sampling_freq]['period']).astype('str'),
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
        df.loc[time_period - 1, 'on_time_delivery_rate'])):
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
        fixedrange = True
    )
    return delivery_time_fig

def plot_stacked_bar(categories : dict):
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
                {cat}
            </div>
        """)
    html_code = f"""
    <style>
    .bar-container {{
        width: 100%;
        height: 7pt;
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

otd_rate_fig = plot_otd_rate(df)
with st.container(border = True):
    st.write(otd_rate_fig)

fct_orders = get_fct_orders()
fct_orders = fct_orders[
    fct_orders.order_approved_at.between(
        time_period.to_timestamp(), 
        time_period.to_timestamp() + DateOffset(freq_map[sampling_freq]['n_months']), inclusive= 'left')
]



with st.container(border = True):
    st.toggle(
    "Split View",
    key="is_split_by_on_time",
    help="Toggle split by On Time vs. Late",
    )

    # Generate and display the figure below the header
    delivery_time_fig = plot_delivery_time(
        fct_orders, st.session_state.is_split_by_on_time
    )
    st.write(delivery_time_fig)
    plot_stacked_bar({'blue' : 0.3, 'red' : 0.4, '34' : 0.3})