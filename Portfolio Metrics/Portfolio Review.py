# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 12:28:49 2024

@author: serw1
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from fpdf import FPDF

#Custome
from Volatility_and_Expected_Return import GBM_Simulation
from Interactive_Graph import int_candlestickgraph
from Stock_Metrics import stock_metrics

f_dir = r"D:/Professional_WorkTools/Github/RodWal-Portfolio/Open Positions.xlsx"

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Position Profitability', 0, 1, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 11)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(0)
        
    def section_title(self, title):
        self.set_font('Arial', "", 10)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(5)
        
    def subsection_title(self, title):
        self.set_font('Arial', "", 8)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(0)
        

    def add_images(self, image_paths):
        col_width = 95  # Adjust column width as needed
        x_positions = [5, 100]  # X positions for the two columns
        y_position = self.get_y()
        for i, image_path in enumerate(image_paths):
            col = i % 2
            if col == 0 and i > 0:
                y_position += 70  # Adjust row height as needed
            self.image(image_path, x=x_positions[col], y=y_position, w=105)
            if col == 1:
                self.ln(70)  # Move to the next row after two images
        self.ln(-8)  # Reduced line spacing after images

    def add_table(self, csv_path):
        self.ln(5)
        self.set_font('Arial', '', 7)
        table = pd.read_csv(csv_path)
        col_width = self.w / (len(table.columns) + 1.5)  # Adjust column width
        row_height = self.font_size * 1.5
        table_width = col_width * len(table.columns)
        x_start = (self.w - table_width) / 2  # Center the table

        # Add table headers
        self.set_xy(x_start, self.get_y())
        self.set_font('Arial', 'B', 7)
        for col in table.columns:
            self.cell(col_width, row_height, col, border=1, align='C')
        self.ln(row_height)

        # Add table rows
        self.set_font('Arial', '', 7)
        for row in table.itertuples(index=False):
            self.set_x(x_start)
            for cell in row:
                self.cell(col_width, row_height, str(cell), border=1, align='C')
            self.ln(row_height)
        self.ln(5)  # Reduced line spacing after images




# REad
portfolio_df = pd.read_excel(f_dir)
positiondate_df = portfolio_df.sort_values(by = ["Date"], ascending = False).drop_duplicates(subset = ["Ticket"])
open_positions_df = portfolio_df[["Ticket","Value","Volume"]].groupby(["Ticket"]).sum()
open_positions_df["Avg Price"] = open_positions_df["Value"]/open_positions_df["Volume"]
open_positions_df = pd.merge(open_positions_df,positiondate_df[["Ticket","Date","Chapter"]], on = "Ticket")


current_date = datetime.now()
T = 1 # Horizon Years
simulations = 100000# Number of simulations
adjusted_return = 1
open_position_view = "Both"
PP = 0 # Percentile graphs


pdf = PDF()
chapter_list = list(set(open_positions_df["Chapter"]))

for chapter in chapter_list[:]:
    mini_open_positions_df = open_positions_df.loc[open_positions_df["Chapter"]==chapter]
    pdf.add_page()
    pdf.chapter_title(chapter+" Portfolio")
    
    #Generate Financial Tables & Stock Metrics
    financials = []
    metrics = []
    names = []
    symbols = []
    
    #Add Companies' financials
    for item in mini_open_positions_df.loc[:].index:
        position = open_positions_df.loc[item]   
        ticker = position.Ticket #Stock Symbol
        finance, metric, name = stock_metrics(ticker)
        financials.append(finance)
        metrics.append(metric)
        names.append(name)
        symbols.append(ticker)
    
    #Add Stock Metrics
    df_metric = pd.DataFrame()
    for symbol, metric in zip(symbols,metrics):
        minidf = pd.read_csv(metric)
        minidf["Symbol"] = symbol
        df_metric = pd.concat([df_metric,minidf], ignore_index= True)
    metric_path = "Resources/Financials_Chapter_"+chapter+".csv"
    df_metric.to_csv(metric_path,index=False)
    pdf.add_table(metric_path)
        
    
        
    
    print(chapter)
    

    for item in mini_open_positions_df.loc[:].index:
        position = open_positions_df.loc[item]    
        ticker = position.Ticket #Stock Symbol
        position_price = position["Avg Price"]
        pdf.add_page()
        pdf.section_title('Price Evolution for '+ticker+" - Open Position: "+str(position_price.round(2)))
        profitability_table = []
        price_img = []
        dist_img = []
        subsection = ["1 Year Maturity","90-Days Maturity","4-Weeks Maturity"]
        for t, vdays,pdays,subsec in zip([1,90/365,4/52],[720,360,120],[364,120,90],subsection):
            start_date = current_date -timedelta(days = vdays) # Volatility Study Range, start date
            end_date = position.Date # Volatility Study Range, start date
            
            start_plotdate = current_date - timedelta(days = pdays)
            start_plotdate = end_date-timedelta(days = vdays) if start_plotdate >= end_date else start_plotdate
            start_date = start_date - timedelta(days = vdays) if abs((end_date - start_date).days)<7*4 else start_date
            end_dateplot = current_date + timedelta(days = 1)
        
            projection_img, distribution_img, maturity_csv = GBM_Simulation(ticker,start_date,end_date,start_plotdate,end_dateplot,simulations,adjusted_return,position_price,t,open_position_view,PP)
            
            price_img.append(projection_img)
            dist_img.append(distribution_img)
            profitability_table.append(maturity_csv)
    
            #pdf.subsection_title('Price Evolution with '+chapter)
            #pdf.add_images([projection_img, distribution_img])
            #pdf.add_table(maturity_csv)
        
        for price,dist,subsec in zip(price_img,dist_img,subsection):
            pdf.subsection_title('Price Evolution with '+subsec)
            pdf.add_images([price, dist])
        
        pdf.add_page()
        for table,subsec in zip(profitability_table,subsection):
            
            pdf.subsection_title('Price Evolution with '+subsec)
            #pdf.add_images([projection_img, distribution_img])
            pdf.add_table(table)
            

pdf.output('pricing_report.pdf')     

