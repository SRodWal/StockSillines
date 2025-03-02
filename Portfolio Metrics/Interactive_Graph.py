import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime as dt
import pandas as pd

# Define the start date for fetching historical data
start_date = dt.datetime(2024, 1, 1)

# Define the stock symbols
symbol_list = ["TSM", "AEP", "MSFT", "PEP", "WMT", "NEE", "QCOM"]

def plot_candlestick_pe_ratio_volume_chart(symbol, start_date):
    # Fetch historical data
    ticker = yf.Ticker(symbol)
    name = ticker.info["longName"]
    data = ticker.history(start=start_date, interval="1wk")
    
    # Fetch quarterly earnings data
    quarterly_earnings = ticker.quarterly_earnings
    
    # Check if quarterly earnings data is available
    if quarterly_earnings is not None and not quarterly_earnings.empty:
        # Create a DataFrame for the P/E ratio
        pe_data = pd.DataFrame(data['Close'])
        pe_data['Quarterly EPS'] = None
        
        for date in pe_data.index:
            # Find the most recent quarterly earnings date
            recent_earnings_date = quarterly_earnings[quarterly_earnings.index <= date].index.max()
            if pd.notna(recent_earnings_date):
                pe_data.loc[date, 'Quarterly EPS'] = quarterly_earnings.loc[recent_earnings_date, 'Earnings']
        
        # Calculate P/E ratio
        pe_data['P/E Ratio'] = pe_data['Close'] / pe_data['Quarterly EPS']
    else:
        # If no quarterly earnings data, use trailing twelve months EPS for P/E ratio
        pe_data = pd.DataFrame(data['Close'])
        pe_data['P/E Ratio'] = data['Close'] / ticker.info['epsTrailingTwelveMonths']
    
    # Calculate Accumulation/Distribution Line (A/D Line)
    def accumulation_distribution_line(df):
        ad_line = []
        ad_val = 0
        for i in range(len(df)):
            clv = ((df['Close'][i] - df['Low'][i]) - (df['High'][i] - df['Close'][i])) / (df['High'][i] - df['Low'][i])
            ad_val += clv * df['Volume'][i]
            ad_line.append(ad_val)
        return ad_line
    
    data['A/D Line'] = accumulation_distribution_line(data)
    
    # Fetch financial data (TTM, last 5 years revenues and CFO)
    financials = ticker.financials.T
    cashflow = ticker.cashflow.T
    FCF_name = cashflow.columns[0]
    FCF_YoY = FCF_name+" YoY%"
    
    # Calculate YoY growth for revenues and CFO
    financials['Revenue YoY Growth'] = financials['Total Revenue'].pct_change()
    cashflow[FCF_YoY] = cashflow[FCF_name].pct_change()
    
    # Create the figure with five subplots (candlestick, P/E ratio, volume distribution, A/D Line, financials)
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.05, subplot_titles=(f'{name} Stock Price', 'P/E Ratio', 'Volume vs. Traded Price', 'Accumulation/Distribution Line', 'Financials (TTM, Revenue, FCF, YoY Growth)'))
    
    # Add candlestick chart (subplot 1)
    fig.add_trace(go.Candlestick(x=data.index,
                                 open=data['Open'],
                                 high=data['High'],
                                 low=data['Low'],
                                 close=data['Close'],
                                 name='Price'), row=1, col=1)

    # Add P/E ratio area chart (subplot 2)
    fig.add_trace(go.Scatter(x=pe_data.index, y=pe_data['P/E Ratio'], mode='lines', line=dict(color='blue'), name='P/E Ratio'), row=2, col=1)

    # Add volume vs. traded price distribution (subplot 3)
    fig.add_trace(go.Histogram(x=data['Close'], y=data['Volume'], histfunc='sum', nbinsx=50, name='Volume Distribution', marker=dict(color='orange')), row=3, col=1)

    # Add A/D Line (subplot 4)
    fig.add_trace(go.Scatter(x=data.index, y=data['A/D Line'], mode='lines', line=dict(color='green'), name='A/D Line'), row=4, col=1)

    ## Add financials (TTM, Revenue, CFO, YoY Growth) chart (subplot 5)
    #fig.add_trace(go.Bar(x=financials.index, y=financials['Total Revenue'], name='Total Revenue'), row=5, col=1)
    #fig.add_trace(go.Bar(x=cashflow.index, y=cashflow[FCF_name], name='FCF'), row=5, col=1)
    #fig.add_trace(go.Scatter(x=financials.index, y=financials['Revenue YoY Growth'], mode='lines+markers', line=dict(color='blue'), name='Revenue YoY Growth',yaxis = "y2"), row=5, col=1)
    #fig.add_trace(go.Scatter(x=cashflow.index, y=cashflow[FCF_YoY], mode='lines+markers', line=dict(color='green'), name='FCF YoY Growth', yaxis = "y2"), row=5, col=1)
    
    # Customize layout with zoom, pan, and sliders
    fig.update_layout(
        title=f'{name} Stock Price, P/E Ratio, Volume Distribution, A/D Line, and Financials',
        xaxis_title='Date',
        yaxis_title='Price',
        template='plotly_dark',
        xaxis_rangeslider_visible=False,
        xaxis=dict(
            rangeslider=dict(
                visible=False  # Show the range slider
            ),
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            ),
            fixedrange=False  # Enable zooming and panning on X-axis
        ),
        yaxis=dict(
            autorange=True  # Enable auto-scaling on Y-axis
        ),
    )
    
    fig.update_yaxes(title_text='P/E Ratio', row=2, col=1, autorange=True)
    fig.update_yaxes(title_text='Volume', row=3, col=1, autorange=True)
    fig.update_yaxes(title_text='A/D Line', row=4, col=1, autorange=True)
    #fig.update_yaxes(title_text='Financials', row=5, col=1, autorange=True)
    
    # Show the chart
    fig.show()
    fig.write_html(name + "_stock_prices_pe_ratio_volume_ad_financials.html")

