import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime as dt
import pandas as pd
from sklearn.cluster import KMeans
import numpy as np

# Define the start date for fetching historical data
start_date = dt.datetime(2022, 1, 1)

# Define the stock symbols
symbol_list = ["TSM", "AEP", "MSFT", "PEP", "WMT", "NEE", "QCOM"]
interval = "1wk"

def calculate_pe_ratio(ticker, interval, start_date):
    data = ticker.history(start=start_date, interval=interval)
    
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
    
    return pe_data

def calculate_ad_line(df):
    """Calculate the Accumulation/Distribution Line (A/D Line)."""
    ad_line = []
    ad_val = 0
    for i in range(len(df)):
        clv = ((df['Close'][i] - df['Low'][i]) - (df['High'][i] - df['Close'][i])) / (df['High'][i] - df['Low'][i])
        ad_val += clv * df['Volume'][i]
        ad_line.append(ad_val)
    return ad_line

def cluster_analysis(data):
    """Perform K-Means clustering on volumes and traded prices."""
    # Prepare the data for clustering
    clustering_data = data[['Close', 'Volume']]
    clustering_data = clustering_data.dropna()
    
    # Normalize the data
    clustering_data_normalized = (clustering_data - clustering_data.mean()) / clustering_data.std()
    
    # Perform K-Means clustering
    kmeans = KMeans(n_clusters=4)  # You can adjust the number of clusters
    kmeans.fit(clustering_data_normalized)
    
    # Add cluster labels to the data
    clustering_data['Cluster'] = kmeans.labels_
    clustering_data['Date'] = clustering_data.index
    
    return clustering_data

def plot_candlestick_pe_ratio_volume_chart(symbol, start_date, interval):
    # Fetch historical data
    ticker = yf.Ticker(symbol)
    name = ticker.info["longName"]
    data = ticker.history(start=start_date, interval=interval)
    
    # Perform cluster analysis
    clustering_data = cluster_analysis(data)
    
    # Calculate Accumulation/Distribution Line (A/D Line)
    data['A/D Line'] = calculate_ad_line(data)
    
    # Create the figure with five subplots (candlestick, P/E ratio, volume distribution, A/D Line, clusters)
    fig = make_subplots(rows=5, cols=1, shared_xaxes=True, vertical_spacing=0.05, subplot_titles=(f'{name} Stock Price', 'P/E Ratio', 'Volume vs. Traded Price', 'Accumulation/Distribution Line', 'Clusters'))
    
    # Add candlestick chart (subplot 1)
    fig.add_trace(go.Candlestick(x=data.index,
                                 open=data['Open'],
                                 high=data['High'],
                                 low=data['Low'],
                                 close=data['Close'],
                                 name='Price'), row=1, col=1)
    
    # Calculate P/E ratio
    pe_data = calculate_pe_ratio(ticker, interval, start_date)
    # Add P/E ratio area chart (subplot 2)
    fig.add_trace(go.Scatter(x=pe_data.index, y=pe_data['P/E Ratio'], mode='lines', line=dict(color='blue'), name='P/E Ratio'), row=2, col=1)

    # Add volume vs. traded price distribution (subplot 3)
    fig.add_trace(go.Histogram(x=data['Close'], y=data['Volume'], histfunc='sum', nbinsx=25, name='Volume Distribution', marker=dict(color='orange')), row=3, col=1)

    # Add A/D Line (subplot 4)
    fig.add_trace(go.Scatter(x=data.index, y=data['A/D Line'], mode='lines', line=dict(color='green'), name='A/D Line'), row=4, col=1)
    
    # Add clustering results with dates (subplot 5)
    for cluster_id in sorted(clustering_data['Cluster'].unique()):
        cluster_trace = go.Scatter(
            x=clustering_data[clustering_data['Cluster'] == cluster_id]['Date'],
            y=clustering_data[clustering_data['Cluster'] == cluster_id]['Volume'],
            mode='markers',
            text=clustering_data[clustering_data['Cluster'] == cluster_id]['Close'],  # Adding traded prices as text labels
            marker=dict(color=cluster_id, colorscale='Viridis'),
            name=f'Cluster {cluster_id}'
        )
        fig.add_trace(cluster_trace, row=5, col=1)
    
    # Add dropdown filter for clusters
    cluster_buttons = [
        dict(
            method="update",
            label=f"Cluster {cluster_id}",
            args=[
                {"visible": [True] * 4 + [cluster_id == cid for cid in clustering_data['Cluster'].unique()]},
                {"title": f"Cluster {cluster_id} of {name}"}
            ]
        ) for cluster_id in sorted(clustering_data['Cluster'].unique())
    ]
    cluster_buttons.append(
        dict(
            method="update",
            label="All Clusters",
            args=[
                {"visible": [True] * len(fig.data)},
                {"title": f"All Clusters of {name}"}
            ]
        )
    )
    fig.update_layout(
        updatemenus=[dict(
            buttons=cluster_buttons,
            direction="down",
            showactive=True
        )]
    )
    
    # Customize layout with zoom, pan, and sliders
    fig.update_layout(
        title=f'{name} Stock Price, P/E Ratio, Volume Distribution, A/D Line, and Clusters',
        xaxis_title='Date',
        yaxis_title='Price',
        template='plotly_dark',
        xaxis=dict(
            rangeslider=dict(visible=False),  # Hide the range slider
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
        yaxis=dict(autorange=True)  # Enable auto-scaling on Y-axis
    )
    fig.update_yaxes(title_text='P/E Ratio', row=2, col=1, autorange=True)
    fig.update_yaxes(title_text='Volume', row=3, col=1, autorange=True)
    fig.update_yaxes(title_text='A/D Line', row=4, col=1, autorange=True)
    fig.update_yaxes(title_text='Clusters', row=5, col=1, autorange=True)
    
    # Show the chart
    fig.show()
    fig.write_html(f"{name}_stock_prices_clusters.html")
