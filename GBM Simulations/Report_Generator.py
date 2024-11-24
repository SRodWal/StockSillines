# Import Custom Modules
from GBM_Simulations_GUI import GBMS, price_probability
from FinalPrice_DisFitting import Dist_Fitting, plot_probability_evolution
import plotly.io as pio
import pandas as pd

# Import Modules
import sys
from PyQt5.QtWidgets import QApplication, QDialog

# Define the main function to generate the dashboard
def generate_dashboard(price_target):
    # Fetch and Simulate Data
    r_mon, v_mon, r_yr, v_yr, df_simulations, fig = GBMS()

    # Generate Distribution Fitting Plot
    fig_dist = Dist_Fitting(df_simulations, 3, "Altria - MO")
    pio.write_html(fig_dist, file='final_prices_histogram.html', auto_open=True)

    # Generate Probability Evolution Plot
    fig_evo = plot_probability_evolution(df_simulations, price_target=price_target, tolerance=0.05*price_target)
    pio.write_html(fig_evo, file='Price_Evolution.html', auto_open=True)
    return fig, fig_dist, fig_evo
# Check if the script is run directly
if __name__ == "__main__":
    #app = QApplication(sys.argv)  # Initialize the QApplication
    generate_dashboard()
    #print("Expected Parameters:")
    #print(pd.DataFrame({"Monthly Return": r_mon, "Montly Volatility:" : v_mon,"Annual Return" : r_yr, "Annual Volatility": v_yr}))
    #sys.exit(app.exec_())  # Start the event loop for the GUI
