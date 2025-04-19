import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib 

data = pd.read_csv('clean_dataset.csv')
data1 = pd.read_csv('new_dataset.csv') 

X = data.drop(columns=['unitPrice']) 
y = data['unitPrice']  
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Train size: {X_train.shape}, Test size: {X_test.shape}")

model = LinearRegression()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)  
mse = mean_squared_error(y_test, y_pred)  
rmse = np.sqrt(mse)  
r2 = r2_score(y_test, y_pred) 
print(f"📌 MAE: {mae:.2f}")
print(f"📌 MSE: {mse:.2f}")
print(f"📌 RMSE: {rmse:.2f}")
print(f"📌 R² Score: {r2:.2f}")

joblib.dump(model, 'linear_regression_model.pkl')
loaded_model = joblib.load('linear_regression_model.pkl')

predicted_price = loaded_model.predict(data1)
print(f" Прогнозируемая цена: {predicted_price[0]:.2f}")