import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QCalendarWidget, QListWidget, QListWidgetItem
from PyQt5.QtCore import QDate
import plotly.graph_objs as go
import plotly.io as pio
from scipy import stats
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Pool

class InputDialog(QDialog):
    def __init__(self, chapters):
        super().__init__()
        self.setWindowTitle('Input Dialog')
        self.setGeometry(100, 100, 400, 300)

        # max_days_map
        self.max_days_map = {'5m': 60-1, '15m': 60-1, '1h': 730-1, '1d': 3650}

        layout = QVBoxLayout()

        # Chapter Selection
        self.chapter_label = QLabel('Select the chapters:')
        self.chapter_list = QListWidget()
        self.chapter_list.setSelectionMode(QListWidget.MultiSelection)
        for chapter in chapters:
            item = QListWidgetItem(chapter)
            self.chapter_list.addItem(item)
        layout.addWidget(self.chapter_label)
        layout.addWidget(self.chapter_list)

        # Interval Selection
        self.interval_label = QLabel('Enter the interval (5m, 15m, 1h, 1d):')
        self.interval_combo = QComboBox()
        self.interval_combo.addItems(['5m', '15m', '1h', '1d'])
        self.interval_combo.currentIndexChanged.connect(self.update_max_days)
        layout.addWidget(self.interval_label)
        layout.addWidget(self.interval_combo)

        # Plot Interval Selection
        self.plot_interval_label = QLabel('Enter the plot interval (5m, 15m, 1h, 1d):')
        self.plot_interval_combo = QComboBox()
        self.plot_interval_combo.addItems(['5m', '15m', '1h', '1d'])
        self.plot_interval_combo.currentIndexChanged.connect(self.update_max_days)
        layout.addWidget(self.plot_interval_label)
        layout.addWidget(self.plot_interval_combo)

        # Length of Simulation
        self.sim_length_label = QLabel('Enter the length of the simulation in days:')
        self.sim_length_input = QLineEdit()
        layout.addWidget(self.sim_length_label)
        layout.addWidget(self.sim_length_input)

        # Calendar for Start Date Selection
        self.start_date_label = QLabel('Select Start Date for Data:')
        self.start_date_calendar = QCalendarWidget()
        self.start_date_calendar.setGridVisible(True)
        self.start_date_calendar.setMaximumDate(QDate.currentDate())
        layout.addWidget(self.start_date_label)
        layout.addWidget(self.start_date_calendar)

        # Calendar for Plot Start Date Selection
        self.plot_start_date_label = QLabel('Select Plot Start Date:')
        self.plot_start_date_calendar = QCalendarWidget()
        self.plot_start_date_calendar.setGridVisible(True)
        self.plot_start_date_calendar.setMaximumDate(QDate.currentDate())
        layout.addWidget(self.plot_start_date_label)
        layout.addWidget(self.plot_start_date_calendar)

        # Submit Button
        self.submit_button = QPushButton('Submit')
        self.submit_button.clicked.connect(self.submit)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def update_max_days(self):
        interval = self.interval_combo.currentText()
        plot_interval = self.plot_interval_combo.currentText()

        if interval in self.max_days_map:
            max_days = self.max_days_map[interval]
            self.start_date_calendar.setMinimumDate(QDate.currentDate().addDays(-max_days))
        
        if plot_interval in self.max_days_map:
            max_days = self.max_days_map[plot_interval]
            self.plot_start_date_calendar.setMinimumDate(QDate.currentDate().addDays(-max_days))

    def submit(self):
        self.chapters = [item.text() for item in self.chapter_list.selectedItems()]
        self.interval = self.interval_combo.currentText()
        self.plot_interval = self.plot_interval_combo.currentText()
        self.sim_length = float(self.sim_length_input.text())
        self.start_date = self.start_date_calendar.selectedDate().toString('yyyy-MM-dd')
        self.plot_start_date = self.plot_start_date_calendar.selectedDate().toString('yyyy-MM-dd')

        self.accept()

def fetch_data(ticker, start_date, interval):
    # Fetch price data
    data = yf.download(ticker, start=start_date, interval=interval, auto_adjust=False)
    if data.empty:
        raise ValueError(f"{ticker}: No price data found for the given date range and interval.")
    
    # Fetch ticker information
    ticker_info = yf.Ticker(ticker).info
    short_name = ticker_info.get('shortName', 'N/A')  # Get shortName, use 'N/A' if not available
    
    """
    #Fetch earnings data
    earnings_data = yf.Ticker(ticker).financials
    if earnings_data.empty:
        raise ValueError(f"{ticker}: No earnings data found for the given date range.")
    #Calcula PE Ratio  
    data['P/E Ratio'] = data['Adj Close'] / earnings_data['Earnings per Share']['ttm']
    """

    return data['Close'], short_name,

#Generates a random walk 
def geometric_brownian_motion(S0, mu, sigma, T, dt, num_steps, end_datetime, interval):
    t = np.linspace(0, T, num_steps)
    W = np.random.standard_normal(size=num_steps)
    W = np.cumsum(W) * np.sqrt(dt)
    X = (mu - 0.5 * sigma ** 2) * t + sigma * W
    S = S0 * np.exp(X)
    
    timestamps = generate_timestamps(end_datetime, num_steps, interval)
    
    # Ensure timestamps align with the length of S
    if len(timestamps) < len(S):
        S = S[:len(timestamps)]
    elif len(timestamps) > len(S):
        timestamps = timestamps[:len(S)]
    
    return timestamps, S

def generate_timestamps(start_datetime, num_steps, interval):
    timestamps = []
    current_datetime = start_datetime
    if interval == '5m':
        delta = timedelta(minutes=5)
    elif interval == '15m':
        delta = timedelta(minutes=15)
    elif interval == '1h':
        delta = timedelta(hours=1)
    elif interval == '1d':
        delta = timedelta(days=1)
    
    for _ in range(num_steps):
        if interval in ['5m', '15m', '1h']:
            if current_datetime.weekday() < 5 and 9 <= current_datetime.hour < 16:
                timestamps.append(current_datetime)
            current_datetime += delta
            while current_datetime.weekday() >= 5 or not (9 <= current_datetime.hour < 16):
                current_datetime += delta
        elif interval == '1d':
            if current_datetime.weekday() < 5:
                timestamps.append(current_datetime)
            current_datetime += delta
            while current_datetime.weekday() >= 5:
                current_datetime += delta
    return timestamps

#Output statistical of N GBM Simulations
def simulate_once(S0, mu, sigma, T, dt, num_steps, end_datetime, interval):
    _, S = geometric_brownian_motion(S0, mu, sigma, T, dt, num_steps, end_datetime, interval)
    return S

def GMB_Simulations(S0, mu, sigma, T, dt, NSimulations, end_datetime, interval):
    num_steps = int(T / dt)
    timestamps, _ = geometric_brownian_motion(S0, mu, sigma, T, dt, num_steps, end_datetime, interval)
    
    #Use ProcessPoolExecutor for parallel simulation
    #with ProcessPoolExecutor() as executor:
    #    all_simulations = list(executor.map(simulate_once, [S0] * NSimulations, [mu] * NSimulations,[sigma] * NSimulations, [T] * NSimulations, [dt] * NSimulations,[num_steps] * NSimulations, [end_datetime] * NSimulations, [interval] * NSimulations))
    #Use Multiprocessing
    #with Pool() as pool:
    #   all_simulations = pool.starmap(simulate_once, 
    #                                  [(S0, mu, sigma, T, dt, num_steps, end_datetime, interval)] * NSimulations)
    
    # Convert to DataFrame for easier manipulation and calculation
    #df_simulations = pd.DataFrame(all_simulations)
    
    #Use For for all simulations
    price_path = []
    for n in range(0,NSimulations):
        #price_path.append(np.concatenate((np.array([S0]),simulate_once(S0, mu, sigma, T, dt, num_steps, end_datetime, interval))))
        price_path.append(simulate_once(S0, mu, sigma, T, dt, num_steps, end_datetime, interval))
    df_simulations = pd.DataFrame(price_path)
    
    
    # Ensure columns match `timestamps`
    #if len(timestamps) == df_simulations.shape[1]:
    #    df_simulations.columns = timestamps
    #else:
    #    raise ValueError("Mismatch between timestamps and simulation results dimensions.")
    
    # Calculate statistics
    percentiles_5 = df_simulations.apply(lambda x: np.percentile(x, 5), axis=0)
    percentiles_25 = df_simulations.apply(lambda x: np.percentile(x, 25), axis=0)
    percentiles_50 = df_simulations.apply(lambda x: np.percentile(x, 50), axis=0)
    percentiles_75 = df_simulations.apply(lambda x: np.percentile(x, 75), axis=0)
    percentiles_95 = df_simulations.apply(lambda x: np.percentile(x, 95), axis=0)
    median = df_simulations.median(axis=0)
    mean = df_simulations.mean(axis=0)
    
    return {
        'percentiles_5': percentiles_5,
        'percentiles_25': percentiles_25,
        'percentiles_50': percentiles_50,
        'percentiles_75': percentiles_75,
        'percentiles_95': percentiles_95,
        'median': median,
        'mean': mean,
        'df_simulations': df_simulations,
    }


    
def price_probability(df_simulations,price_target,tolerance):
    # Calculate probability within the specified range
    lower_bound = price_target - tolerance
    upper_bound = price_target + tolerance
    within_range = df_simulations.apply(lambda x: ((x >= lower_bound) & (x <= upper_bound)).mean(), axis=0)
    above_range = df_simulations.apply(lambda x: ((x >= price_target)).mean(), axis=0)
    below_range = df_simulations.apply(lambda x: ((x <= price_target)).mean(), axis=0)
    
    # Create a single DataFrame to join the three ranges
    probability_df = pd.DataFrame({
        'Within Range': within_range,
        'Above Target': above_range,
        'Below Target': below_range
    })
    
    return probability_df
    

        
    # Calculate probability within the specified range
    lower_bound = price_target - tolerance
    upper_bound = price_target + tolerance
    within_range = df_simulations.apply(lambda x: ((x >= lower_bound) & (x <= upper_bound)).mean(), axis=0)
    above_range = df_simulations.apply(lambda x: ((x >= price_target)).mean(), axis=0)
    below_range = df_simulations.apply(lambda x: ((x <= price_target)).mean(), axis=0)
    
    # Create a single DataFrame to join the three ranges
    probability_df = pd.DataFrame({
        'Within Range': within_range,
        'Above Target': above_range,
        'Below Target': below_range
    })
    
    return probability_df

def GBMS(ticker,interval,plot_interval,T,start_date,plot_start_date):
    
    interval_map = {'5m': 1/288, '15m': 1/96, '1h': 1/24, '1d': 1}
    max_days_map = {'5m': 60-1, '15m': 60-1, '1h': 730-1, '1d': 3650} # 3650 days (10 years) for daily data
    monthly_returns = {'5m': 1692, '15m': 564, '1h': 136.5, '1d': 21}
    yearly_returns = {'5m': 19656, '15m': 6552, '1h': 1638, '1d': 252}
    
    

    
    
    """
    ticker = input("Enter the ticker symbol: ")
    interval = input("Enter the interval (5m, 15m, 1h, 1d): ")
    if interval not in interval_map:
        print("Invalid interval. Choose from 5m, 15m, 1h, 1d.")
        return
    plot_interval = input("Enter the plot interval (5m, 15m, 1h, 1d): ")
    if plot_interval not in interval_map:
        print("Invalid interval. Choose from 5m, 15m, 1h, 1d.")
        return
    T = float(input("Enter the length of the simulation in days: "))
    #Select Calendar with limited ranged
    max_days = max_days_map[interval]
    start_date = get_date("Select Start Date for Data", max_days)
    plot_start_date = get_date("Select Plot Start Date", 3650)
    """
    

    dt = interval_map[interval]
    
    monthly_factor = monthly_returns[interval]
    yearly_factor = yearly_returns[interval]
    
   

    # Fetch data
    data, Name = fetch_data(ticker, start_date, interval)
    returns = data.pct_change().dropna()
    S0 = data.iloc[-1].iloc[-1]

    #Translate interval return to log returns
    log_returns = np.log(returns + 1)
    mu = log_returns.mean().iloc[0]
    sigma = log_returns.std().iloc[0]
    end_datetime = max(data.index)
    
    #Simulate 1 random walk
    num_steps = int(T / dt)
    t, _ = geometric_brownian_motion(S0, mu, sigma, T, dt, num_steps, end_datetime, interval)
    
    
    #Statistical Simulations of GBM
    NSimulations = 10000
    GBMS_dict = GMB_Simulations(S0, mu, sigma, T, dt, NSimulations, end_datetime, interval)
    data = pd.DataFrame({
        '5th Percentile': GBMS_dict['percentiles_5'],
        '25th Percentile': GBMS_dict['percentiles_25'],
        '50th Percentile': GBMS_dict['percentiles_50'],
        '75th Percentile': GBMS_dict['percentiles_75'],
        '95th Percentile': GBMS_dict['percentiles_95'],
        'Median': GBMS_dict['median'],
        'Mean': GBMS_dict['mean']
    }, index=t)
    # Plotting the data
    
    mean_final_price = GBMS_dict["df_simulations"].iloc[:,-1].mean()
    # Calculate the absolute difference between each simulation's final price and the mean final price
    final_prices = GBMS_dict["df_simulations"].iloc[:,-1]
    differences = np.abs(final_prices - mean_final_price)

    # Find the index of the simulation with the smallest difference
    closest_index = differences.idxmin()

    # Extract the price path closest to the mean final price
    closest_path = GBMS_dict["df_simulations"].loc[closest_index]
    
    
    simulated_data = pd.DataFrame({'Time': t,'Simulated Price': closest_path})
    simulated_data.set_index('Time', inplace=True)
    
    
    
    
    plt.figure(figsize=(14, 8))
    plt.fill_between(data['95th Percentile'].index, data['5th Percentile'],data['95th Percentile'], alpha = 0.1, color = "gray")
    plt.fill_between(data['95th Percentile'].index, data['25th Percentile'],data['75th Percentile'], alpha = 0.1, color = "gray")
    plt.fill_between(data['95th Percentile'].index, data['50th Percentile'],data['Mean'], alpha = 0.1, color = "gray")
    
    plt.plot(data['5th Percentile'], label='95th Percentile', linestyle=':', color='gray')
    plt.plot(data['25th Percentile'], label='75th Percentile', linestyle=':', color='grey')
    plt.plot(data['50th Percentile'], label='50th Percentile', linestyle=':', color='grey')
    plt.plot(data['75th Percentile'], linestyle=':', color='grey')
    plt.plot(data['95th Percentile'], linestyle=':', color='gray')
    plt.plot(data['Median'], label='Median', linestyle='-', color='black', linewidth=2)
    plt.plot(data['Mean'], label='Mean', linestyle='-', color='purple', linewidth=2)
    
    plt.title('GBM Simulations: Percentiles, Median, and Mean')

    

    #print(simulated_data)

    #HistData
    Hist_data, _ = fetch_data(ticker,plot_start_date,plot_interval)
    
    # Plotting
    #plt.figure(figsize=(14, 8))
    plt.plot(Hist_data, label='Historical Prices', linestyle='-', color='blue')
    plt.plot(simulated_data, label='Simulated Prices', linestyle='--', color='green')
    plt.title(f'Historical and Simulated Prices for {ticker}')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    #plt.show()
    

    
    # Plotting with Plotly
    fig = go.Figure()

    # Plot historical data
    fig.add_trace(go.Scatter(x=Hist_data.index, y=Hist_data[ticker].tolist(), mode='lines', name='Historical Prices', line=dict(color='blue')))

    # Plot simulated data
    fig.add_trace(go.Scatter(x=simulated_data.index, y=simulated_data['Simulated Price'].tolist(), mode='lines', name='Simulated Prices', line=dict(color='red', dash='dash')))
    # Add percentiles, median, and mean to the plot
    fig.add_trace(go.Scatter(x=t, y=GBMS_dict['percentiles_5'].tolist(), mode='lines', name='5th Percentile', line=dict(color='gray', dash="dot"), legendgroup = "5th Percentiles"))
    fig.add_trace(go.Scatter(x=t, y=GBMS_dict['percentiles_25'].tolist(), mode='lines', name='25th Percentile', line=dict(color='orange', dash='dash'), legendgroup = "25th Percentiles"))
    fig.add_trace(go.Scatter(x=t, y=GBMS_dict['percentiles_50'].tolist(), mode='lines', name='50th Percentile', line=dict(color='green', dash='dash'), legendgroup = "Metrics"))
    fig.add_trace(go.Scatter(x=t, y=GBMS_dict['percentiles_75'].tolist(), mode='lines', name='75th Percentile', line=dict(color='orange', dash='dash'), legendgroup = "25th Percentiles"))
    fig.add_trace(go.Scatter(x=t, y=GBMS_dict['percentiles_95'].tolist(), mode='lines', name='95th Percentile', line=dict(color='gray', dash='dot'), legendgroup = "5th Percentiles"))
    fig.add_trace(go.Scatter(x=t, y=GBMS_dict['median'].tolist(), mode='lines', name='Median', line=dict(color='black'), legendgroup = "Metrics"))
    fig.add_trace(go.Scatter(x=t, y=GBMS_dict['mean'].tolist(), mode='lines', name='Mean', line=dict(color='purple'), legendgroup = "Metrics"))

    
    fig.update_layout(title='GBMS - '+Name+": Annual Returns "+str(round(mu*yearly_factor*100,2))+"%, Monthly "+str(round(mu*monthly_factor*100,2))+"%; Annual Volatility "+str(round(sigma * np.sqrt(yearly_factor)*100,2))+"%. Monthly "+str(round(sigma * np.sqrt(monthly_factor)*100,2))+"%",
                      xaxis_title='Time',
                      yaxis_title='Price',
                      legend=dict(x=0, y=1.0),
                      autosize=False,
                      width=1450,
                      height=800)

    # Save plot to HTML
    #pio.write_html(fig, file='GBM_simulations_plot.html', auto_open=True)
    return mu*monthly_factor,mu*yearly_factor, sigma * np.sqrt(monthly_factor),sigma * np.sqrt(yearly_factor),GBMS_dict["df_simulations"],fig
    
"""
if __name__ == '__main__':

    #GUI Input Parameters
    app = QApplication(sys.argv)
    dialog = InputDialog()
    if dialog.exec() == QDialog.Accepted:
        # Access input parameters after the dialog is accepted
        ticker = dialog.ticker
        interval = dialog.interval
        plot_interval = dialog.plot_interval
        T = dialog.sim_length
        start_date = dialog.start_date
        plot_start_date = dialog.plot_start_date
            
        print(f'Ticker: {ticker}')
        print(f'Interval: {interval}')
        print(f'Plot Interval: {plot_interval}')
        print(f'Simulation Length (days): {T}')
        print(f'Start Date: {start_date}')
        print(f'Plot Start Date: {plot_start_date}')

    r_mon, v_mon, r_yr, v_yr, df_simulations, fig = GBMS(ticker,interval,plot_interval,T,start_date,plot_start_date)
    """


