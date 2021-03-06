#Yahoo Finance & Data collection
import yfinance as yf
import pandas as pd
import os, requests_cache
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
StockList = ["BA.MX","FSLR.MX","0jn9n.MX", "APA.MX", "VISTAA.MX","SNPN.MX","RDSB.MX","CDEV.MX","NMKA.MX","NEMAKA.MX","ASMLN.MX",
             "CSIQN.MX", "JKSN.MX","SUN.MX","HON.MX","SIEN.MX","GE.MX","TSLA.MX","TMN.MX","SONYN.MX","HMCN.MX","HYUDN.MX","HOMEX.MX",
             "ARA.MX","CADUA.MX","NKLA.MX","LEN.MX","SWK.MX","MCN.MX","NESNN.MX","PG.MX","FAST.MX","MCK.MX","AAPL.MX","TSMN.MX","NVDA.MX",
             "SMSNN.MX","AMD.MX","IPGP.MX","SPCE.MX","MITSN.MX","TXT.MX","QCOM.MX","RIGN.MX","SPKN.MX","RSGA.MX","LINN.MX","AIN.MX",
             "APD.MX","AMZN.MX","WMT.MX","SHOPN.MX","AEROMEX.MX","UPS.MX","RYAAYN.MX","NEE.MX","IBEN.MX","SO.MX","XEL.MX","FANG.MX",
             "SEDGN.MX"] #List of Stocks


#Export lists of stocks
#tickerdf = pd.DataFrame()
#tickerdf["Ticker"] = StockList
#tickerdf["Name"] = NameList
#tickerdf.to_excel("TickersList.xlsx", index = False)

###Objective folder

##Writes data in excels
#create excels for each ticker: Historic (daily), Last 6 months (5min intervals)
def Historical_TickerGraph( StockList ):
    session = requests_cache.CachedSession('yfinance.cache')
    session.headers['User-agent'] = 'my-program/1.0'
    
    for ticker in StockList:
        filedir = os.getcwd()
        datadir = filedir+"\\DATA"  
        Rawdata = yf.Ticker(ticker, session = session) #Retrieves all stock information
        datainf = Rawdata.info
        print(ticker)
        tickername = datainf["longName"]
        if "/" in tickername:
            tickername = tickername.replace("/","")
        if "." in tickername:    
            tickername = tickername.replace(".","")
        currency = datainf["currency"]
        data = Rawdata.history(period = "max") # Stock daily historic data
        textdate = [time.strftime("%m/%d/%Y") for time in data.index]
        Histperiod = textdate[0]+" - "+textdate[-1]
        x = data.index.tolist()
        candledata = go.Candlestick(x = x, open = data.Open, high = data.High,low = data.Low, close = data.Close, name = "Pricing")
        volumedata = go.Scatter(x = x, y = data.Volume, name = "Volume", yaxis = "y2")
        divdata = go.Scatter(x=x, y= data.Dividends, name = "Dividends", yaxis = "y3")
        fig = make_subplots(specs = [[{"secondary_y": True}]])
        fig.add_trace(candledata)
        fig.add_trace(volumedata, secondary_y = True)
        fig.add_trace(divdata, secondary_y = True)
        fig.update_layout(title = "Historical Data: "+tickername+"  ---   "+" Ticker:"+ticker.upper(), yaxis_title = currency, xaxis_title = "Period "+Histperiod,                       )
        fig.write_html(datadir+"\\Hist_"+tickername+".html")

def Ticker_Portfolio( StockList):
    session = requests_cache.CachedSession('yfinance.cache')
    session.headers['User-agent'] = 'my-program/1.0'
    
    #List of columns
    NameList = []
    SectorList = []
    IndustryList = []
    CountryList = []
    CharList = ["longName", "sector", "industry", "country"]
    Columns = [NameList, SectorList, IndustryList, CountryList]
    ColumnsList = ["Name", "Symbol", "Sector", "Industry", "Country"]
    for ticker in StockList:
        print("Downloading: "+ticker)
        TIKinfo = yf.Ticker(ticker, session = session).info
        for char, cols in zip(CharList, Columns):
            cols.append(TIKinfo[char])
        print("Operation successful")    
    df = pd.DataFrame()
    Columns = [NameList, StockList, SectorList, IndustryList, CountryList]
    for name, cols in zip(ColumnsList, Columns):
            df[name] = cols
        
    df.to_excel("Portfolio.xlsx")
    
#Historical_TickerGraph(StockList)
#Ticker_Portfolio(StockList)
    



