import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime as dt

startyear = 2020
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
fig = make_subplots(rows=1, cols=2, shared_yaxes=False, subplot_titles=("Candlestick", "Volume"))

# Add candlestick chart (subplot 1)
fig.add_trace(go.Candlestick(x=tsm_data.index,
                             open=tsm_data['Open'],
                             high=tsm_data['High'],
                             low=tsm_data['Low'],
                             close=tsm_data['Close'],
                             name='Price'))

# Add volume bar chart (subplot 2)
fig.add_trace(go.Bar(x=tsm_data.index,
                     y=tsm_data['Volume'],
                     name='Volume'))

# Customize layout
fig.update_layout(title=f"{stock_symbol} Stock Price and Volume",
                  xaxis_title="Date",
                  yaxis_title="Price / Volume",
                  template="plotly_dark")

# Show or save the figure
fig.show()


# Save the interactive plot as an HTML file
fig.write_html("tsm_stock_prices.html")

print("Interactive plot saved as 'tsm_stock_prices.html'")

