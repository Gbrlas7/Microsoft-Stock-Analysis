import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

file_path = r"C:\Users\HP\Documents\Downloads\Microsoft Inference\MSFT_stock_2021.xlsx"
df = pd.read_excel(file_path)

# Convert Date column to datetime objects for clean x-axis formatting
df['Date'] = pd.to_datetime(df['Date'])

plt.figure(figsize=(12, 6))
plt.plot(df['Date'], df['Close'], color='#1f77b4', linewidth=1.5)

# Add titles and labels
plt.title('Microsoft (MSFT) Historical Daily Closing Prices', fontsize=16, fontweight='bold')
plt.xlabel('Year', fontsize=12)
plt.ylabel('Closing Price (USD)', fontsize=12)

# Format the grid and x-axis dates
plt.grid(True, linestyle='--', alpha=0.7)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.gca().xaxis.set_major_locator(mdates.YearLocator(base=4)) # Place a tick every 4 years
plt.xticks(rotation=45)

plt.tight_layout()
plt.savefig('4_msft_prices_history.png', dpi=300)
plt.close() # Change this to plt.show() if you want it to pop up on your screen!

print(">>> Saved: 4_msft_prices_history.png")
