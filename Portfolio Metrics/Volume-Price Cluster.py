import yfinance as yf
import plotly.graph_objects as go
from plotly.graph_objs import Scatter3d
import datetime as dt
import pandas as pd
from sklearn.cluster import KMeans
import numpy as np

# Define the start date for fetching historical data
start_date = dt.datetime(2021, 1, 1)

# Define the start date for fetching historical data
start_date = dt.datetime(2024, 1, 1)

# Define the stock symbols
symbol_list = ["TSM", "AEP", "MSFT", "PEP", "WMT", "NEE", "QCOM"]
interval = "1d"
symbol = "YPF"


def cluster_analysis(data):
    """Perform K-Means clustering on volumes, traded prices, and time."""
    # Prepare the data for clustering
    clustering_data = data[['Close', 'Volume']]
    clustering_data = clustering_data.dropna()
    #clustering_data['Time'] = np.arange(len(clustering_data))
    
    # Normalize the data
    clustering_data_normalized = (clustering_data - clustering_data.mean()) / clustering_data.std()
    
    # Perform K-Means clustering
    kmeans = KMeans(n_clusters=2)  # You can adjust the number of clusters
    kmeans.fit(clustering_data_normalized)
    
    # Add cluster labels to the data
    clustering_data['Cluster'] = kmeans.labels_
    clustering_data['Date'] = clustering_data.index
    
    return clustering_data

def plot_3d_clusters(symbol, start_date, interval):
    # Fetch historical data
    ticker = yf.Ticker(symbol)
    name = ticker.info["longName"]
    data = ticker.history(start=start_date, interval=interval)
    
    # Perform cluster analysis
    clustering_data = cluster_analysis(data)
    
    # Calculate median values for each cluster
    cluster_medians = clustering_data.groupby('Cluster').median()
    
    # Create 3D scatter plot for clustering results
    scatter3d = Scatter3d(
        x=clustering_data['Close'],
        y=clustering_data['Date'],
        z=clustering_data['Volume'],
        mode='markers',
        marker=dict(
            size=5,
            color=clustering_data['Cluster'],
            colorscale='Viridis',
            opacity=0.8
        ),
        text=clustering_data['Date'],  # Adding dates as text labels
        name='Clusters'
    )
    
    # Create 3D scatter plot for median points
    median_scatter3d = Scatter3d(
        x=cluster_medians['Close'],
        y=cluster_medians['Date'],
        z=cluster_medians['Volume'],
        mode='markers',
        marker=dict(
            size=10,
            color='red',
            symbol='x'
        ),
        text=[f"Cluster {i} Median" for i in cluster_medians.index],
        name='Cluster Medians'
    )
    
    # Create layout for 3D plot
    layout_3d = go.Layout(
        title=f'{name} 3D Clustering: Price, Time, and Volume with Medians',
        scene=dict(
            xaxis=dict(title='Price'),
            yaxis=dict(title='Date'),
            zaxis=dict(title='Volume')
        ),
        template='simple_white',
        updatemenus=[dict(
            buttons=[
                dict(
                    method="update",
                    label=f"Cluster {cluster_id}",
                    args=[{"visible": [True, True] + [cluster_id == cid for cid in clustering_data['Cluster'].unique()]}]
                ) for cluster_id in sorted(clustering_data['Cluster'].unique())
            ] + [dict(
                method="update",
                label="All Clusters",
                args=[{"visible": [True, True] + [True] * len(clustering_data['Cluster'].unique())}]
            )],
            direction="down",
            showactive=True
        )]
    )
    
    # Show 3D clustering plot
    fig_3d = go.Figure(data=[scatter3d, median_scatter3d], layout=layout_3d)
    fig_3d.show()
    fig_3d.write_html(f"{name}_stock_prices_3D_Cluster.html")

plot_3d_clusters(symbol, start_date, interval)
