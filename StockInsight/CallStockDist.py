import pandas as pd
import numpy as np
import yfinance as yf
import pandas_datareader as pdr
import datetime as dt
import matplotlib.pyplot as plt

# A script to analyze stock prices and temproral changes.


#Define input variables
StockList = ["TSM"]
TimeWindow = [dt.datetime(2019,1,1),dt.datetime.now()]

#Collect data
df = pdr.get_data_yahoo(StockList[0],TimeWindow[0],TimeWindow[1])
print(df)


