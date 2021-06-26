#Yahoo Finance & Data collection
import yfinance as yf
import pandas as pd
#Numeric and data treatment
import numpy as np
import datetime as dt
import seaborn as sb
#Graphs
import matplotlib.pyplot as plt
import plotly.graph_pbjects as go

# A script to analyze stock prices and temproral changes.
# This is designed for medium-short term investments (No interdaily informacion)


#Define input variables
StockList = ["TSM"]
TimeWindow = [dt.datetime(2019,1,1),dt.datetime.now()]

#Collect data
df = pdr.get_data_yahoo(StockList[0],TimeWindow[0],TimeWindow[1])

#Initial Stock description:
    #Valume movement graphs
sb.lineplot(data = df, x = "Date", y = "Volume")
plt.title("Volume - "+StockList[0])
    #Prices daily range
    #Initial & closeing values
    




