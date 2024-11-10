import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf

from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense , Dropout, LSTM
from pandas.tseries.offsets import BDay
from sklearn.metrics import mean_squared_error
from math import sqrt

# # Colab'a bir PNG dosyası yükleyin
# uploaded = files.upload()

# # Eğer birden fazla dosya yüklüyorsanız, dosya adını doğru dosya adıyla değiştirin
# file_name = list(uploaded.keys())[0]

# # PNG dosyasını okuyun
# logo_img = mpimg.imread(file_name)

# # Dosyayı /content dizinine taşıyın
# !mv {file_name} /content/

# Kullanıcıdan hisse senedi sembolünü al
symbol = input("Stok name : ")

# Hisse senedi verilerini al
data = yf.download(symbol, start='2023-01-01', end='2024-02-01' )


#Data preperation
scaler = MinMaxScaler(feature_range=(0,1))
scaled_data = scaler.fit_transform(data['Close'].values.reshape(-1,1))

prediction_days = 30

X_train = []
y_train = []

for x in range(prediction_days, len(scaled_data)):
    X_train.append(scaled_data[x-prediction_days:x,0])
    y_train.append(scaled_data[x,0])

X_train, y_train = np.array(X_train), np.array(y_train)
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

model = Sequential()
model.add(LSTM(units=50,return_sequences=True,input_shape=(X_train.shape[1], 1)))
model.add(Dropout(0.2))
model.add(LSTM(units=50,return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(units=50,return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(units=50))
model.add(Dropout(0.2))
model.add(Dense(units=1))
model.compile(optimizer='adam',loss='mean_squared_error')


###############################################################
model.fit(X_train, y_train, epochs=500, batch_size=32, verbose=0)
###############################################################

test_data =yf.download(symbol, period="1y")
actual_prices=test_data['Close'].values

total_dataset = pd.concat((data['Close'], test_data['Close']), axis=0)

model_inputs = total_dataset[len(total_dataset)-len(test_data) - prediction_days:].values
model_inputs = model_inputs.reshape(-1,1)
model_inputs  = scaler.transform(model_inputs)

#Make prediction on test data

x_test = []

for x in range(prediction_days, len(model_inputs)):
    x_test.append(model_inputs[x-prediction_days:x,0])

x_test = np.array(x_test)
x_test = np.reshape(x_test,(x_test.shape[0], x_test.shape[1],1))


predicted_prices = model.predict(x_test)
predicted_prices = scaler.inverse_transform(predicted_prices)


actual_dates = test_data.index[-len(test_data):]

last_date = actual_dates[-1]
future_dates = []
count = 0
while count < 5:
    last_date += BDay(1)
    if last_date.weekday() < 5:
        future_dates.append(last_date)
        count += 1


#Predict next days
predicted_prices_future = []

a = 1
while a <= 5:
    real_data = [model_inputs[len(model_inputs) + a - prediction_days:len(model_inputs) + a, 0]]
    real_data = np.array(real_data)
    real_data = np.reshape(real_data, (real_data.shape[0], real_data.shape[1], 1))

    prediction = model.predict(real_data)
    prediction = scaler.inverse_transform(prediction)

    predicted_prices_future.append(prediction[0][0])

    a += 1
predicted_prices_future= np.array(predicted_prices_future)

def plot_prediction_with_dates(dates, actual_data, predicted_data, future_dates, future_prediction):
    plt.figure(figsize=(16, 4))
    plt.style.use('fivethirtyeight')
    #plt.imshow(logo_img, extent=[-0.5, 16-0.5, -0.5, 4-0.5])
    plt.plot(dates[-len(actual_data):], actual_data, color='blue', label='Actual Stock Price: ' + str(test_data['Close'][-1]))
    plt.plot(dates[len(actual_data)-30:], predicted_data[-30:], color='red', label='Predicted Stock Prices '+ 'day(0) :' + str(predicted_prices[-1]))
    plt.plot(future_dates, predicted_prices_future * np.ones(len(future_dates)), color='orange', label='Forecasted (day+' + str(a) + ')) : ' + str(prediction[0][0]))
    plt.title("Stock Price Prediction")
    plt.xlabel("Date")
    plt.ylabel("Stock Price")
    plt.legend()
    plt.xticks(rotation=45)
    plt.show()

plot_prediction_with_dates(actual_dates, test_data['Close'], predicted_prices, future_dates, predicted_prices_future)

rmse = sqrt(mean_squared_error(test_data['Close'], predicted_prices))
print("Root Mean Squared Error (RMSE):", rmse)