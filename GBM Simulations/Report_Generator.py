# Import Custom Modules
from GBM_Simulations_GUI import GBMS, price_probability
from FinalPrice_DisFitting import Dist_Fitting, plot_probability_evolution
import plotly.io as pio
import pandas as pd
import tkinter as tk
from tkinter import simpledialog
# Import Modules
import sys
from PyQt5.QtWidgets import QApplication, QDialog

# Custom Modules
def Selector(lst):
    def on_select():
        nonlocal selected_items, risk_aversion
        selected_items = [lst[i] for i in lb.curselection()]
        risk_aversion = slider.get() / 100  # Convert to a value between 0 and 1
        root.destroy()
    
    selected_items = []
    risk_aversion = 0.5  # Default value
    
    root = tk.Tk()
    root.title("Multi-Select List")
    root.geometry("400x400")

    lb = tk.Listbox(root, selectmode=tk.MULTIPLE)
    for item in lst:
        lb.insert(tk.END, item)
    lb.pack(padx=10, pady=10)

    slider_label = tk.Label(root, text="Risk Aversion (0: Max Returns, 100: Min Risk):")
    slider_label.pack(pady=10)

    slider = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL)
    slider.pack(pady=10)

    select_button = tk.Button(root, text="Select", command=on_select)
    select_button.pack(pady=10)

    root.mainloop()
    
    return selected_items, risk_aversion

# Read data from Excel
f_dir = r"D:/Professional_WorkTools/Github/StockSillines/Open Positions.xlsx"
portfolio_df = pd.read_excel(f_dir)
portfolio_df = portfolio_df[["Chapter", "Ticker", "Volume", "Price", "Expected Return QoQ%", "Volatility", "Value","Target Price"]]
Selected_Chapters, risk_aversion = Selector(list(set(portfolio_df.Chapter)))
df = portfolio_df.loc[portfolio_df.Chapter.isin(Selected_Chapters)].drop("Chapter", axis=1)

# Define the main function to generate the dashboard
def generate_dashboard(price_target):
    # Fetch and Simulate Data
    r_mon, v_mon, r_yr, v_yr, df_simulations, fig = GBMS()
    KPIs = {"Annual Return" : r_yr, "Annual Volatility" : v_yr, "Monthly Return" : r_mon, "Monthly Volatility" : v_mon}

    # Generate Distribution Fitting Plot
    fig_dist = Dist_Fitting(df_simulations, 3, "Altria - MO")
    pio.write_html(fig_dist, file='final_prices_histogram.html', auto_open=True)

    # Generate Probability Evolution Plot
    fig_evo = plot_probability_evolution(df_simulations, price_target=price_target, tolerance=0.05*price_target)
    pio.write_html(fig_evo, file='Price_Evolution.html', auto_open=True)
    return fig, fig_dist, fig_evo, KPIs
# Check if the script is run directly
if __name__ == "__main__":
    #app = QApplication(sys.argv)  # Initialize the QApplication
    generate_dashboard(80)
    #print("Expected Parameters:")
    #print(pd.DataFrame({"Monthly Return": r_mon, "Montly Volatility:" : v_mon,"Annual Return" : r_yr, "Annual Volatility": v_yr}))
    #sys.exit(app.exec_())  # Start the event loop for the GUI
