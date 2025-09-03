import pandas as pd

# Example DataFrame with both text and numbers
data = {
    'Ticker': ['AAPL', 'GOOGL', 'MSFT'],
    'Return': [0.1234, 0.5678, 0.9101],
    'Comments': ['Good stock', 'High growth', 'Stable']
}
df = pd.DataFrame(data)

# Function to format numerical values as percentages
def format_percentage(x):
    if isinstance(x, (int, float)):
        return f"{x * 100:.2f}%"
    return x

# Apply formatting to the DataFrame
df = df.applymap(format_percentage)

print(df)
