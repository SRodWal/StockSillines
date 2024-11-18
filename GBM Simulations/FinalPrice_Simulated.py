import plotly.graph_objs as go
import plotly.figure_factory as ff
import plotly.io as pio
import pandas as pd
from GBM_Simulations_GUI import price_probability

def plot_histogram_with_stats(df_simulations, ticker):
    final_prices = df_simulations.iloc[:, -1]
    close_price = df_simulations.iloc[0,0]
    
    Tol = 0.025 # Tolerance

    # Calculate percentiles, mean, and median
    percentiles_1 = final_prices.quantile(0.01)
    percentiles_5 = final_prices.quantile(0.05)
    percentiles_25 = final_prices.quantile(0.25)
    percentiles_50 = final_prices.quantile(0.50)
    percentiles_75 = final_prices.quantile(0.75)
    percentiles_95 = final_prices.quantile(0.95)
    percentiles_99 = final_prices.quantile(0.99)
    mean = final_prices.mean()
    median = final_prices.median()
    
    # Calculate probabilities of final prices
    pr_p5 = price_probability(df_simulations, percentiles_5,percentiles_5*Tol).iloc[-1,0]
    pr_p95 = price_probability(df_simulations, percentiles_95,percentiles_95*Tol).iloc[-1,0]
    pr_p25 = price_probability(df_simulations, percentiles_25,percentiles_25*Tol).iloc[-1,0]
    pr_p75 = price_probability(df_simulations, percentiles_75,percentiles_75*Tol).iloc[-1,0]
    pr_mean = price_probability(df_simulations, mean,mean*Tol).iloc[-1,0]
    pr_median = price_probability(df_simulations, median,median*Tol).iloc[-1,0]
    pr_close = price_probability(df_simulations, close_price,close_price*Tol).iloc[-1,0]

    # Create the histogram
    hist_data = [final_prices]
    group_labels = ['Final Prices']

    # Create the histogram plot
    fig = ff.create_distplot(hist_data, group_labels, bin_size=Tol*close_price, show_rug=False, show_hist=True)

    # Find the maximum density for setting y-axis limit
    max_density = max([trace['y'].max() for trace in fig.data if trace['type'] == 'scatter'])
    y_max = 1.2 * max_density

    # Add lines for percentiles, mean, median, and close price
    fig.add_trace(go.Scatter(x=[percentiles_5, percentiles_5], y=[0, y_max], mode='lines', name='5th Percentile - PR: '+str(round(pr_p5*100,1))+"%", line=dict(color='gray', dash='dot')))
    fig.add_trace(go.Scatter(x=[percentiles_25, percentiles_25], y=[0, y_max], mode='lines', name='25th Percentile - PR: '+str(round(pr_p25*100,1))+"%", line=dict(color='orange', dash='dot')))
    fig.add_trace(go.Scatter(x=[percentiles_50, percentiles_50], y=[0, y_max], mode='lines', name='50th Percentile - PR: '+str(round(pr_median*100,1))+"%", line=dict(color='green', dash='dot')))
    fig.add_trace(go.Scatter(x=[percentiles_75, percentiles_75], y=[0, y_max], mode='lines', name='75th Percentile - PR: '+str(round(pr_p75*100,1))+"%", line=dict(color='orange', dash='dot')))
    fig.add_trace(go.Scatter(x=[percentiles_95, percentiles_95], y=[0, y_max], mode='lines', name='95th Percentile - PR: '+str(round(pr_p95*100,1))+"%", line=dict(color='grey', dash='dot')))
    fig.add_trace(go.Scatter(x=[mean, mean], y=[0, y_max], mode='lines', name='Mean - PR: '+str(round(pr_mean*100,1))+"%", line=dict(color='purple')))
    #fig.add_trace(go.Scatter(x=[median, median], y=[0, y_max], mode='lines', name='Median', line=dict(color='black')))
    fig.add_trace(go.Scatter(x=[close_price, close_price], y=[0, y_max], mode='lines', name='Close Price - PR: '+str(round(pr_close*100,1))+"%", line=dict(color='brown', dash='dash')))

    fig.update_layout(
        title=f'Histogram of Simulated Final Prices for {ticker}',
        xaxis_title='Final Price (in USD)',
        yaxis_title='Density',
        height=600,
        width=900,
        legend=dict(x=0.8, y=1.2),
        xaxis=dict(showgrid=True, range=[percentiles_1, percentiles_99]),  # Set x-axis range to 1st to 99th percentile
        yaxis=dict(showgrid=True, range=[0, y_max])
    )

    try:
        # Save plot to HTML
        pio.write_html(fig, file='final_prices_histogram.html', auto_open=True)
    except Exception as e:
        print(f"Error saving HTML file: {e}")

# Example usage
ticker = 'V'
close_price = df_simulations.iloc[0,0]  # Example close price
# Assuming df_simulations is already defined
plot_histogram_with_stats(df_simulations, ticker)
