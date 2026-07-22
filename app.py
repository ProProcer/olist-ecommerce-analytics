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

def get_delivery_time(start, duration = 'monthly'):
    pass

# On time delivery rate figure
def plot_otd_rate(df):
    df['on_time_delivery_perc'] = df['on_time_delivery_rate'] * 100

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
    
    otd_rate_fig = px.line(
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

    x_ticks = pd.Series(np.concatenate(
        (df.timestamp,
        df.timestamp.max() + DateOffset(months = n_months) * np.array([1, 2, 3]))
    ))

    otd_rate_fig.update_xaxes(
        range = (
            current_timestamp - DateOffset(months = n_months * 2, days = 1/3 * 30 * n_months), 
            current_timestamp + DateOffset(months = n_months * 2, days = 1/3 * 30 * n_months)
        ),
        tickvals = x_ticks,
        ticktext = x_ticks.dt.to_period(freq_map[sampling_freq]['period']).astype('str'),
        fixedrange = True,
        title_text = None
    )

    otd_rate_fig.update_yaxes(
        range = (min(df.loc[time_period, 'on_time_delivery_perc'] - 1, 85), 100),
        fixedrange = True,
        title_text = None
    )
    
    otd_rate_fig.add_traces(
        (
        go.Scatter(
            x = [current_timestamp],
            y = [df.loc[time_period, 'on_time_delivery_perc']],
            marker_color = "#000001"
        ),
        go.Scatter(
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


delivery_time_fig = px.box(df, x = 'total_delivery_days', orientation = 'h')
otd_rate_fig = plot_otd_rate(df)
st.write(otd_rate_fig)
st.write(delivery_time_fig)