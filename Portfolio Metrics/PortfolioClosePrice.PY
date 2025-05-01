import pandas as pd
import yfinance as yf

# Read the input Excel file
input_file = "Open Positions.xlsx"  # Replace with your file name
output_file = "updated_close_prices.xlsx"

# Load the Excel file
df = pd.read_excel(input_file)

# Create a new DataFrame for the output
output_data = []

# Fetch the latest close price for each ticker
for index, row in df.iterrows():
    ticker = row["Ticker"]
    chapter = row["Chapter"]
    name = row["Name"]
    
    try:
        stock = yf.Ticker(ticker)
        latest_close = stock.history(period="1wk")["Close"].iloc[-1]  # Get the latest close price
    except Exception as e:
        latest_close = f"Error: {e}"  # Handle errors gracefully
    
    # Append updated data
    output_data.append({
        "Chapter": chapter,
        "Name": name,
        "Ticker": ticker,
        "Close Price": latest_close
    })

# Convert to a DataFrame
output_df = pd.DataFrame(output_data)

# Save the updated data to a new Excel file
output_df.to_excel(output_file, index=False)

print(f"Updated close prices have been saved to {output_file}")