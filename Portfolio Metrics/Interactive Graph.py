import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import kaleido
import datetime as dt

startyear = 2024
startmonth = 1 
startday = 1
start = dt.datetime(startyear, startmonth, startday)

## Sets today

now = dt.datetime

# Define the stock symbol and date range
stock_symbol = 'TSM'
start_date = start
end_date = now.now()

# Fetch historical data
tsm_data = yf.download(stock_symbol, start=start_date, end=end_date)

# Create a figure with two subplots (shared x-axis)
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, subplot_titles=('Candlestick', 'Volume'))

# Add candlestick chart (subplot 1)
fig.add_trace(go.Candlestick(x=tsm_data.index,
                             open=tsm_data['Open'],
                             high=tsm_data['High'],
                             low=tsm_data['Low'],
                             close=tsm_data['Close'],
                             name='Price'),row=1, col=1)

# Add volume bar chart (subplot 2)
fig.add_trace(go.Bar(x=tsm_data.index,y=tsm_data.Volume,
                     name='Volume'), row=2, col=1)

# Customize layout
# Customize layout
fig.update_layout(title="TSM Stock Price and Volume",
                  xaxis_title="Date",
                  yaxis_title="Price",
                  #yaxis2_title="Volume",
                  template="plotly_dark")

# Show or save the figure
fig.show()

# Save the interactive plot as an HTML file
fig.write_html("tsm_stock_prices.html")
fig.write_image("images\+"+stock_symbol+".png", engine = "kaleido")
fig.write_image("images\+"+stock_symbol+".svg")

print("Interactive plot saved as 'tsm_stock_prices.html'")

from tradingview_ta import TA_Handler, Exchange, Interval

import plotly.graph_objects as go
import numpy as np

np.random.seed(1)
N = 100
x = np.random.rand(N)
y = np.random.rand(N)
colors = np.random.rand(N)
sz = np.random.rand(N) * 30

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=x,
    y=y,
    mode="markers",
    marker=go.scatter.Marker(
        size=sz,
        color=colors,
        opacity=0.6,
        colorscale="Viridis"
    )
))
fig.show()