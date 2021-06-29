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
from plotly.subplots import make_subplots
from plotly.offline import plot
import plotly.express as px


# A script to analyze stock prices and temproral changes.
# This is designed for medium-short term investments (No interdaily informacion)


###Define input variables
StockList = ["BA","FSLR","PCRFY"] #List of Stocks
NameList = ["Boeing Co", "First Solar, Inc", "Panasonic Corp"] # Names of the tickers
period = "5wk" #Time backwards
interval = "5m" # Time between mesurements  

#Export lists of stocks
#tickerdf = pd.DataFrame()
#tickerdf["Ticker"] = StockList
#tickerdf["Name"] = NameList
#tickerdf.to_excel("TickersList.xlsx", index = False)

###Objective folder

##Writes data in excels
#create excels for each ticker: Historic (daily), Last 6 months (5min intervals)
def Historic_TickerGraph( StockList, Namelist ):
    for ticker,name in zip(StockList, NameList):
        filedir = os.getcwd()
        datadir = filedir+"\\DATA"  
        Rawdata = yf.Ticker(ticker) #Retrieves all stock information
        data = Rawdata.history(period = "max") # Stock daily historic data
        textdate = [time.strftime("%m/%d/%Y") for time in data.index]
        Histperiod = textdate[0]+" - "+textdate[-1]
        candledata = go.Candlestick(x = data.index.tolist(), open = data.Open, high = data.High,low = data.Low, close = data.Close, name = "Pricing")
        volumedata = go.Scatter(x = data.index.tolist(), y = data.Volume, name = "Volume", yaxis = "y2")
        fig = make_subplots(specs = [[{"secondary_y": True}]])
        fig.add_trace(candledata)
        fig.add_trace(volumedata, secondary_y = True)
        fig.update_layout(title = "Historical "+name+" stock prices", yaxis_title = "USD", xaxis_title = "Period "+Histperiod,                       )
        fig.write_html(datadir+"\\Hist_"+name+".html")
    





