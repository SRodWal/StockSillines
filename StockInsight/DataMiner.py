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
from plotly.offline import plot
import plotly.express as px


# A script to analyze stock prices and temproral changes.
# This is designed for medium-short term investments (No interdaily informacion)


###Define input variables
StockList = ["BA","FSLR","PCRFY"] #List of Stocks
NameList = ["Boeing Co", "First Solar, Inc", "Panasonic Corp"] # Names of the tickers
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
for ticker,name in zip(StockList, NameList):
    Rawdata = yf.Ticker(ticker) #Retrieves all stock information
    data = Rawdata.history(period = "max") # Stock daily historic data
    textdate = [time.strftime("%m/%d/%Y") for time in data.index]
    Histperiod = textdate[0]+" - "+textdate[-1]
    #data = data.reset_index()
    #candledata = go.Candlestick(x = data["Datetime"] ,open = data["Open"], high = data["High"],low = data["Low"], close = data["Close"])
    candledata = go.Candlestick(x = data.index.tolist(), open = data.Open, high = data.High,low = data.Low, close = data.Close)
    fig = go.Figure(data = [candledata])
    #fig.update_layout(title = "Historic "+name+" stock prices", yaxis_title = "USD", xaxis_title = "Period "+Histperiod, 
     #                 xaxis = dict(tickmode = "array", tickvals = data.reset_index().index.tolist(), ticktext = textdate))
    fig.write_html(datadir+"\\Hist_"+name+".html")
    





