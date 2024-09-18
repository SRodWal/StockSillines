# Geometric Brownian Motion Simulation for Stock Price Projection

## Overview
This project simulates the geometric Brownian motion to project the price walk of a stock. It generates a graph showing the distribution of future prices, including both the open position price/date and the latest adjusted close price/date. This visualization helps compare the current price path with the one projected at the open position price/date.



Additionally, the simulation displays the final price distribution after N days of maturity and the expected gross margins for different percentiles of the final price.

## Features
- **Price Walk Projection**: Simulates the geometric Brownian motion to project future stock prices.
- **Graphical Visualization**: Generates a graph with the distribution of future prices, open position price/date, and latest adjusted close price/date.
- **Final Price Distribution**: Displays the distribution of final prices after N days.
- **Expected Gross Margins**: Calculates and displays the expected gross margins for different percentiles of the final price.

## Example
Price Distribution Simulation:
![2024 09 17 MO](https://github.com/user-attachments/assets/6e73245d-3706-4d7f-a9b4-827b6f4500cc)

Final Price distribution:
![2024 09 17 MO-Dist](https://github.com/user-attachments/assets/4afafa9d-894c-4e01-94d5-0beb4ef07b99)

Projected forward price & profitability:
Altria Group, Inc.; Open position: 51.24 with 140 Days Maturity

  |    | Price Description   |   Forward Price |   Profit Margin (%) |
  |---:|:--------------------|----------------:|--------------------:|
  |  0 | 5th percentile      |           46.1  |              -11.15 |
  |  1 | 25th percentile     |           51.41 |                0.33 |
  |  2 | 45th percentile     |           54.65 |                6.24 |
  |  3 | 50th percentile     |           55.43 |                7.56 |
  |  4 | 65th percentile     |           57.87 |               11.46 |
  |  5 | 75th percentile     |           59.77 |               14.27 |
  |  6 | 95th percentile     |           66.71 |               23.19 |
