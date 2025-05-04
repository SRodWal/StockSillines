import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import kaleido
import datetime as dt

#Use matplotlib for analytics
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc
import pandas as pd

startyear = 2024
startmonth = 1 
startday = 1
start_date = dt.datetime(startyear, startmonth, startday)

symbol_list = ["TSM","AEP","MSFT","PEP","WMT","NEE","QCOM"]
name_list = [x+" - "+yf.Ticker(x).info["longName"] for x in symbol_list]

def int_candlestickgraph(symbol_list,start_date):

## Sets today
    now = dt.datetime

    # Define the stock symbol and date range
    end_date = now.now()
    
    # Fetch historical data
    for stock_symbol in symbol_list:
        ticker = yf.Ticker(stock_symbol)
        info = ticker.info
        hist = ticker.history(period = "1y")
        name = info["longName"]
        tsm_data = yf.download(stock_symbol, start=start_date, end=end_date, interval="1h")
        
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
        
        #Add current position
        purchase_date = "2024-06-17"
        purchase_price = 165.93
        fig.add_trace(go.Scatter(
            x=[hist.index.min(), hist.index.max()],
            y=[purchase_price, purchase_price],
            mode="lines",
            line=dict(color="green", dash="dash"),
            name="Purchase Price"
            ))
        fig.add_trace(go.Scatter(
            x=[purchase_date, purchase_date],
            y=[hist['Low'].min(), hist['High'].max()],
            mode="lines",
            line=dict(color="green", dash="dash"),
            name="Purchase Date"
            ))

        
        
        # Customize layout
        # Customize layout
        fig.update_layout(title=name+" Stock Price and Volume",
                          xaxis_title="Date",
                          yaxis_title="Price",
                          #yaxis2_title="Volume",
                          template="plotly_dark")
        fig.update_yaxes(fixedrange=False)
        # Show or save the figure
        fig.show()
        
        # Save the interactive plot as an HTML file
        fig.write_html(name+"_stock_prices.html")
        #fig.write_image(name+ ".png")
        #fig.write_image(name+".svg")

