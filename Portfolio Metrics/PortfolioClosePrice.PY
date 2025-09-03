import pandas as pd
import yfinance as yf

# Read the input Excel file
input_file = "Open Positions.xlsx"  # Replace with your file name
output_file = "updated_close_prices.xlsx"

# Load the Excel file
df = pd.read_excel(input_file)

# Create a new DataFrame for the output
output_data = []

# Fetch the latest close price, GICS sector, and expected dividend yield for each ticker
for index, row in df.iterrows():
    ticker = row["Ticker"]
    chapter = row["Chapter"]
    name = row["Name"]
    
    try:
        stock = yf.Ticker(ticker)
        latest_close = stock.history(period="1d")["Close"].iloc[-1]  # Get latest close price
        gics_sector = stock.info.get("sector", "Unknown")  # Extract GICS sector
        dividend_yield = stock.info.get("dividendYield", "N/A")  # Fetch dividend yield
        
        # Convert yield to percentage (if available)
        if dividend_yield != "N/A" and dividend_yield is not None:
            dividend_yield = dividend_yield

    except Exception as e:
        latest_close = f"Error: {e}"
        gics_sector = "Unknown"
        dividend_yield = 0

    # Append updated data
    output_data.append({
        "Chapter": chapter,
        "Name": name,
        "Ticker": ticker,
        "Close Price": latest_close,
        "GICS Sector": gics_sector,
        "Expected Dividend Yield %": dividend_yield
    })

# Convert to a DataFrame
output_df = pd.DataFrame(output_data)

# Save the updated data to a new Excel file
output_df.to_excel(output_file, index=False)

print(f"Updated data (including GICS Sector and Expected Dividend Yield) has been saved to {output_file}")