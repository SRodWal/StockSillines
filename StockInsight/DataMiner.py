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
#Import & Export lists of stocks
tickerdf = pd.DataFrame()
tickerdf["Ticker"] = StockList
tickerdf["Name"] = NameList
tickerdf.to_excel("TIckersList.xlsx", index = False)

###Objective folder
datadir = filedir+"\\DATA"  
# Read files in data folder 




