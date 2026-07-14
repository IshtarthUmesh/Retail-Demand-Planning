import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA

# Load dataset
df = pd.read_csv("train.csv", parse_dates=['date'])

# Show available options
print("\nAvailable Stores:", df['store_nbr'].unique())
print("\nAvailable Families:", df['family'].unique())

# User selects store and family
store = int(input("\nEnter store number: "))
family = input("Enter product family: ").strip().upper()

# Filter data
df_filtered = df[(df['store_nbr'] == store) & (df['family'] == family)]
if df_filtered.empty:
    print("\n❌ No data found for that store and family. Please try again.")
    exit()

# Prepare time series
df_filtered = df_filtered[['date', 'sales']].set_index('date').sort_index()
df_filtered.index = pd.DatetimeIndex(df_filtered.index).to_period("D")

# Plot raw data
plt.figure(figsize=(12, 5))
plt.plot(df_filtered.index.to_timestamp(), df_filtered['sales'], label=f"{family} - Store {store}")
plt.title("Daily Sales")
plt.xlabel("Date")
plt.ylabel("Sales")
plt.legend()
plt.tight_layout()
plt.savefig("raw_sales_plot.png", dpi=300)
plt.show()

# ADF test
result = adfuller(df_filtered['sales'])
print(f"\nADF Statistic: {result[0]}")
print(f"p-value: {result[1]}")
if result[1] > 0.05:
    print("❌ Series is non-stationary. Applying differencing.")
    df_stationary = df_filtered.diff().dropna()
else:
    print("✅ Series is stationary.")
    df_stationary = df_filtered

# Re-test if differenced
if result[1] > 0.05:
    result_diff = adfuller(df_stationary['sales'])
    print(f"\nDifferenced ADF Statistic: {result_diff[0]}")
    print(f"Differenced p-value: {result_diff[1]}")

# Fit ARIMA
print("\nTraining ARIMA(1,1,1) model...")
model = ARIMA(df_filtered, order=(1, 1, 1))
model_fit = model.fit()
print(model_fit.summary())

# Forecast next 30 days
forecast = model_fit.forecast(steps=30)
forecast.index = forecast.index.to_timestamp()

# Plot forecast
plt.figure(figsize=(12, 5))
plt.plot(df_filtered.index.to_timestamp()[-60:], df_filtered['sales'][-60:], label="Actual Sales")
plt.plot(forecast.index, forecast, color='red', label="Forecast")
plt.title(f"30-Day Forecast: {family} - Store {store}")
plt.xlabel("Date")
plt.ylabel("Sales")
plt.legend()
plt.tight_layout()
plt.savefig("forecast_plot.png", dpi=300)
plt.show()

# Save forecast to CSV
forecast_df = pd.DataFrame({
    'Date': forecast.index,
    'Forecasted_Sales': forecast.values
})
filename = f"forecast_store{store}_{family.lower()}.csv"
forecast_df.to_csv(filename, index=False)
print(f"\n✅ Forecast saved to: {filename}")
