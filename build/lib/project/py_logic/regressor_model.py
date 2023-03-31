import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from prophet import Prophet
from .preprocess import preprocess_revenue, preprocess_complete

def regressor_model():

    #Load Data
    df = preprocess_revenue()
    #Load feature dataframe
    feature_df = preprocess_complete()
    #Merge dataframes on ds
    df = pd.merge(df,feature_df,how="left")
    #Loading weather prediction data
    weather_forecast = pd.read_csv("../feature_data/finall_pred_weather.csv")
    weather_forecast["ds"] = pd.to_datetime(weather_forecast["ds"])
    weather_forecast["forecast dt iso"] = pd.to_datetime(weather_forecast["forecast dt iso"])
    merged_df = pd.merge(df,feature_df,how="left")

    #Setting variables
    horizon = 16

    #Splitting the data
    split_date = "2022-08-01"
    index_split = df[df["ds"]==split_date].index[0]
    df_train = merged_df.iloc[:index_split]
    df_test = merged_df.iloc[index_split:]
    y_test = pd.DataFrame(df_test["y"])
    weather_index_split = weather_forecast[weather_forecast["forecast dt iso"]==split_date].index[0]
    weather_predict = weather_forecast.iloc[weather_index_split:weather_index_split+horizon,:]
    weather_predict = weather_predict.drop(columns="forecast dt iso")

    #Instatiating  the model
    m = Prophet()

    #Adding regressors/features
    m.add_regressor("temp")
    m.add_regressor("humidity")
    m.add_regressor("wind_speed")
    m.add_regressor("wind_deg")
    m.add_regressor("rain")
    m.add_regressor("clouds")
    m.add_regressor("Holiday")
    m.add_regressor("inflation_rate")
    m.add_regressor("Consumption Climate")
    m.add_regressor("cov_lock")
    m.add_regressor("unemp_Berlin_Mitte")

    m = m.fit(df_train)

    #Creating future dataframe
    future = m.make_future_dataframe(periods=horizon)

    #Adding feature values to future dataframe
    future = pd.merge(future,feature_df,how="left")

    #Update Future Timeframe with prediction weather data instead of historical weather data to prevent overfitting
    cols_to_update = ['temp', 'humidity', 'clouds', 'wind_speed', 'wind_deg', 'rain']
    future.loc[future.index[-(horizon):], cols_to_update] = weather_predict[cols_to_update].values

    #Predicting
    forecast = m.predict(future)
    seven_day_forecast = forecast.tail(horizon)
    seven_day_forecast_slim = seven_day_forecast[["ds","yhat_lower","yhat","yhat_upper"]]
    prediction_forecast = seven_day_forecast_slim
    prediction_forecast["y_true"] = y_test.head(horizon)
    prediction_forecast["error"]=abs(prediction_forecast["yhat"]-prediction_forecast["y_true"])

    return prediction_forecast
