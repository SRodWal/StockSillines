# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 12:28:49 2024

@author: serw1
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

#Custome
from Volatility_and_Expected_Return import GBM_Simulation
from Interactive_Graph import int_candlestickgraph

f_dir = r"D:/Professional_WorkTools/Github/RodWal-Portfolio/Open Positions.xlsx"


# REad
portfolio_df = pd.read_excel(f_dir)
positiondate_df = portfolio_df.sort_values(by = ["Date"], ascending = False).drop_duplicates(subset = ["Ticket"])
open_positions_df = portfolio_df[["Ticket","Value","Volume"]].groupby(["Ticket"]).sum()
open_positions_df["Avg Price"] = open_positions_df["Value"]/open_positions_df["Volume"]
open_positions_df = pd.merge(open_positions_df,positiondate_df[["Ticket","Date"]], on = "Ticket")


current_date = datetime.now()
T = 20/52 # Horizon Years
simulations = 100000# Number of simulations
adjusted_return = 1
open_position_view = "Both"
PP = 0 # Percentile graphs



for item in open_positions_df.loc[9:9].index:
    position = open_positions_df.loc[item]    
    ticker = position.Ticket #Stock Symbol
    position_price = position["Avg Price"]
    
    
    start_date = current_date -timedelta(days = 365) # Volatility Study Range, start date
    end_date = position.Date # Volatility Study Range, start date
    
    start_plotdate = current_date - timedelta(days = 120)
    end_dateplot = current_date + timedelta(days = 1)
    
        
    
    
    GBM_Simulation(ticker,start_date,end_date,start_plotdate,end_dateplot,simulations,adjusted_return,position_price,T,open_position_view,PP)


