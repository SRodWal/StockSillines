# Import Custom Modules
from GBM_Simulations import GBMS, InputDialog, price_probability
from FinalPrice_DisFitting import Dist_Fitting, plot_probability_evolution
import plotly.io as pio
import pandas as pd
import tkinter as tk
from tkinter import simpledialog
import sys
from PyQt5.QtWidgets import QApplication, QDialog
import yfinance as yf

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

def fetch_ticker_info(ticker):
    # Fetch ticker information using yfinance
    ticker_info = yf.Ticker(ticker).info
    short_name = ticker_info.get('shortName', ticker)
    return short_name

def generate_dashboard(price_target, ticker, interval, plot_interval, T, start_date, plot_start_date):
    # Fetch and Simulate Data
    r_mon, r_yr, v_mon, v_yr, df_simulations, fig = GBMS(ticker, interval, plot_interval, T, start_date, plot_start_date)
    KPIs = {"Annual Return": r_yr, "Annual Volatility": v_yr, "Monthly Return": r_mon, "Monthly Volatility": v_mon}

    # Generate Distribution Fitting Plot
    fig_dist = Dist_Fitting(df_simulations, 5, ticker)
    #pio.write_html(fig_dist, file=f'{ticker}_final_prices_histogram.html', auto_open=False)

    # Generate Probability Evolution Plot
    fig_evo = plot_probability_evolution(df_simulations, price_target=price_target, tolerance=0.05 * price_target)
    #pio.write_html(fig_evo, file=f'{ticker}_Price_Evolution.html', auto_open=False)

    return fig, fig_dist, fig_evo, KPIs
"""
def guardar_graficas_html(html_filename, df, tickers_info, figs_dict):
    # Map ticker names to info
    df['Nombre Ticker'] = df['Ticker'].map(tickers_info)

    # Reorder columns to place 'Nombre Ticker' first
    df = df[['Nombre Ticker'] + [col for col in df.columns if col != 'Nombre Ticker']]

    # Convert dataframe to HTML
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write("<h1 id='top'>Geometric Brownian Motion Portfolio Simulation</h1>\n")
        f.write("<ul style='columns: 2;'>\n")
        
        for ticker, short_name in tickers_info.items():
            f.write(f'<li><a href="#{ticker}" style="color:blue;">{ticker} - {short_name}</a></li>\n')
        f.write("</ul>\n\n")

        f.write("<h2>Expected Returns and Volatilities</h2>\n")
        f.write(df.to_html(index=False))  # Convert DataFrame to HTML
        f.write("</div>\n")

        for ticker, figures in figs_dict.items():
            short_name = tickers_info[ticker]
            f.write(f'<a id="{ticker}"></a>\n')
            f.write(f'<h2>{ticker} - {short_name}</h2>\n')
            f.write("<div style='display: flex; justify-content: center;'>\n")
            f.write("<div style='margin-right: 20px;'>\n")
            f.write(figures[0].to_html(full_html=False, include_plotlyjs='cdn'))
            f.write("</div>\n")
            f.write("<div>\n")
            f.write(figures[1].to_html(full_html=False, include_plotlyjs='cdn'))
            f.write(figures[2].to_html(full_html=False, include_plotlyjs='cdn'))
            f.write("</div>\n")
            f.write("</div>\n")
            f.write(f'<br><a href="#top">Ir al inicio</a><br><br>\n')

    print(f"Las gráficas y la tabla han sido guardadas en {html_filename}")
"""    
    
def guardar_graficas_html(html_filename, df, tickers_info, figs_dict):
    # Map ticker names to info
    df['Nombre Ticker'] = df['Ticker'].map(tickers_info)

    # Reorder columns to place 'Nombre Ticker' first
    df = df[['Nombre Ticker'] + [col for col in df.columns if col != 'Nombre Ticker']]
    
    # Function to format numerical values as percentages
    def format_percentage(x):
        if isinstance(x, (int, float)):
            return f"{x * 100:.2f}%"
        return x

    # Apply formatting to the DataFrame
    df = df.applymap(format_percentage)
    
    # Convert dataframe to HTML
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write("<h1 id='top'>Geometric Brownian Motion Portfolio Simulation</h1>\n")
        f.write("<ul style='columns: 2;'>\n")
        
        for ticker, short_name in tickers_info.items():
            f.write(f'<li><a href="#{ticker}" style="color:blue;">{ticker} - {short_name}</a></li>\n')
        f.write("</ul>\n\n")

        f.write("<h2>Expected Returns and Volatilities</h2>\n")
        f.write("<div style='display: flex; flex-direction: column; align-items: center;'>\n")
        f.write(df.to_html(index=False))  # Convert DataFrame to HTML
        f.write("</div>\n")

        for ticker, figures in figs_dict.items():
            short_name = tickers_info[ticker]
            f.write(f'<a id="{ticker}"></a>\n')
            f.write(f'<h2>{ticker} - {short_name}</h2>\n')
            f.write("<div style='display: flex; flex-direction: column; align-items: center;'>\n")
            #f.write("<div style='margin-bottom: 5px;'>\n")
            f.write(figures[0].to_html(full_html=False, include_plotlyjs='cdn'))
            f.write("</div>\n")
            #f.write("<div style='display: flex; justify-content: center;'>\n")
            #f.write("<div style='margin-right: 20px;'>\n")
            f.write("<div style='display: flex; flex-direction: column; align-items: center;'>\n")
            f.write(figures[1].to_html(full_html=False, include_plotlyjs='cdn'))
            f.write("</div>\n")
            f.write("</div>\n")
            f.write("<div style='display: flex; flex-direction: column; align-items: center;'>\n")
            f.write(figures[2].to_html(full_html=False, include_plotlyjs='cdn'))
            f.write("</div>\n")
            f.write("</div>\n")
            f.write("</div>\n")
            f.write(f'<br><a href="#top">Ir al inicio</a><br><br>\n')

    print(f"Las gráficas y la tabla han sido guardadas en {html_filename}")


if __name__ == "__main__":
    # Read Excel Data
    f_dir = r"D:/Professional_WorkTools/Github/StockSillines/Open Positions.xlsx"
    portfolio_df = pd.read_excel(f_dir)
    portfolio_df = portfolio_df[["Chapter", "Ticker", "Volume", "Price", "Expected Return QoQ%", "Volatility", "Value", "Target Price"]]
    
    app = QApplication(sys.argv)
    dialog = InputDialog(list(set(portfolio_df.Chapter)))
    if dialog.exec() == QDialog.Accepted:
        # Access input parameters after the dialog is accepted
        selected_chapters = dialog.chapters
        interval = dialog.interval
        plot_interval = dialog.plot_interval
        T = dialog.sim_length
        start_date = dialog.start_date
        plot_start_date = dialog.plot_start_date

        print(f'Chapters: {selected_chapters}')
        print(f'Interval: {interval}')
        print(f'Plot Interval: {plot_interval}')
        print(f'Simulation Length (days): {T}')
        print(f'Start Date: {start_date}')
        print(f'Plot Start Date: {plot_start_date}')

        # Filter Selected Chapters
        df = portfolio_df.loc[portfolio_df.Chapter.isin(selected_chapters)]
        kpis = []
        figs_dict = {}
        tickers_info = {}

        for chapter in selected_chapters:
            tickers = df.loc[df.Chapter == chapter].Ticker
            price_targets = df.loc[df.Chapter == chapter]["Target Price"]
            for ticker, price_target in zip(tickers, price_targets):
                print(f"Processing Ticker: {ticker}")
                short_name = fetch_ticker_info(ticker)
                tickers_info[ticker] = short_name
                fig, fig_dist, fig_evo, KPI = generate_dashboard(price_target, ticker, interval, plot_interval, T, start_date, plot_start_date)
                figs_dict[ticker] = [fig, fig_dist, fig_evo]
                KPI['Chapter'] = chapter
                KPI['Ticker'] = ticker
                kpis.append(KPI)

        # Create DataFrame for KPIs
        kpi_df = pd.DataFrame(kpis)

        # Generate HTML report
        guardar_graficas_html("GBMS_Report_3M.html", kpi_df, tickers_info, figs_dict)
