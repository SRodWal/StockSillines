#Yahoo Finance & Data collection
import yfinance as yf
import pandas as pd
import os
#Numeric and data treatment
import numpy as np
import datetime as dt
import seaborn as sb
#Graphs
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# A script to analyze stock prices and temproral changes.
# This is designed for medium-short term investments (No interdaily informacion)


###Define input variables
StockList = ["BA","FSLR","HQCL"] #List of Stocks
NameList = ["Boeing Co.", "First Solar, Inc.", "Hanwha Q CELLS Co."] # Names of the tickers
period = "5wk" #Time backwards
interval = "5m" # Time between mesurements  
filedir = os.getcwd()
#Export lists of stocks
#tickerdf = pd.DataFrame()
#tickerdf["Ticker"] = StockList
#tickerdf["Name"] = NameList
#tickerdf.to_excel("TickersList.xlsx", index = False)

###Objective folder
datadir = filedir+"\\DATA"  
##Writes data in excels
#create excels for each ticker: Historic (daily), Last 6 months (5min intervals)
for ticker in StockList:
    data = yf.download(ticker, period = period, interval = interval)
    candledata = [go.Candlestick(x = data.index,open = data["Open"], high = data["High"],low = data["Low"], close = data["Close"])]
    fig = go.Figure(data = candledata)
    fig.show()
    print(data)






