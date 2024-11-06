import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr
import yfinance as yf
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from xgboost import XGBRegressor
from datetime import datetime, timedelta

# Override yfinance
yf.pdr_override()

# Fetch the stock data
df = pdr.get_data_yahoo('BWA', start='2022-04-01', end=datetime.now())
data = df[['Close']]

# Create a lagged feature dataset for XGBoost
look_back = 60
for i in range(1, look_back + 1):
    data[f'lag_{i}'] = data['Close'].shift(i)

# Drop rows with missing values due to lagging
data.dropna(inplace=True)

# Define features and target variable
X = data.drop(columns=['Close']).values
y = data['Close'].values

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.05, shuffle=False)

# Initialize and train the XGBoost model
model = XGBRegressor(objective='reg:squarederror', n_estimators=100, learning_rate=0.1)
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Calculate RMSE for evaluation
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
print(f'RMSE: {rmse}')

# Future forecasting for the next 10 days
future_predictions = []
last_60_days = X_test[-1].reshape(1, -1)

for _ in range(10):
    next_pred = model.predict(last_60_days)[0]
    future_predictions.append(next_pred)
    
    # Update the last_60_days to shift the prediction window
    last_60_days = np.roll(last_60_days, -1)
    last_60_days[0, -1] = next_pred

# Dates for future predictions
last_date = df.index[-1]
future_dates = [last_date + timedelta(days=i) for i in range(1, 11)]
future_df = pd.DataFrame(data={'Date': future_dates, 'Predicted_Close': future_predictions})
future_df.set_index('Date', inplace=True)

# Plot the results
plt.figure(figsize=(16, 6))
plt.title('Stock Price Prediction with XGBoost')
plt.xlabel('Date', fontsize=18)
plt.ylabel('Close Price USD ($)', fontsize=18)
plt.plot(data.index[-len(y_test):], y_test, label='True Price')
plt.plot(data.index[-len(y_test):], y_pred, label='Predicted Price')
plt.plot(future_df.index, future_df['Predicted_Close'], linestyle='dashed', color='red', label='Future Prediction')
plt.legend()
plt.show()
