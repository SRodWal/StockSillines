import pandas as pd
import numpy as np
from math import sqrt
import datetime as dt
import seaborn as sb
import matplotlib.pyplot as plt
import scipy, warnings

import yfinance as yf

warnings.filterwarnings("ignore")

df = yf.Ticker("BA.MX").history( period = "max")
removecols = ["Dividends","Stock Splits","Volume"]
df.drop(removecols, axis = 1, inplace = True)
print(df)





