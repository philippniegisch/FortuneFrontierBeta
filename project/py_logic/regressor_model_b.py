import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from prophet import Prophet
from .preprocess_b import preprocess_revenue, preprocess_complete
from google.cloud import storage
import pandas as pd
import os
import io


def regressor_model():

    #Load Data
    df = preprocess_revenue()
    #Load feature dataframe
    feature_df = preprocess_complete()
    #Merge dataframes on ds
    df = pd.merge(df,feature_df,how="left")
    #Loading weather prediction data
    bucket_name = os.environ.get("BUCKET_NAME")
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob_pred_weather = bucket.blob("feature_data/finall_pred_weather.csv")
    csv_data_pred_weather = blob_pred_weather.download_as_string()
    weather_forecast = pd.read_csv(io.BytesIO(csv_data_pred_weather))
    weather_forecast["ds"] = pd.to_datetime(weather_forecast["ds"])
    weather_forecast["forecast dt iso"] = pd.to_datetime(weather_forecast["forecast dt iso"])
    merged_df = pd.merge(df,feature_df,how="left")
    merged_df['cap'] = 1.2 * df['y'].max()

    #Setting variables
    horizon = 16

    #to enable input from front end / work around for circular import
    from frontend.app_b import prediction_date

    #Splitting the data
    split_date = prediction_date
    index_split = df[df["ds"]==split_date].index[0]
    df_train = merged_df.iloc[:index_split]
    df_test = merged_df.iloc[index_split:]
    y_test = pd.DataFrame(df_test["y"])
    weather_index_split = weather_forecast[weather_forecast["forecast dt iso"]==split_date].index[0]
    weather_predict = weather_forecast.iloc[weather_index_split:weather_index_split+horizon,:]
    weather_predict = weather_predict.drop(columns="forecast dt iso")

    #Instatiating  the model
    m = Prophet(growth = 'logistic', changepoint_prior_scale = 0.1, seasonality_prior_scale = 0.1, seasonality_mode='multiplicative',\
           yearly_seasonality= 12, weekly_seasonality = True)

    #Adding regressors/features
    m.add_regressor("temp")
    m.add_regressor("wind_speed")
    m.add_regressor("wind_deg")
    m.add_regressor("rain")
    m.add_regressor("clouds")
    m.add_regressor("Holiday")
    m.add_regressor("inflation_rate")

    m = m.fit(df_train)

    #Creating future dataframe
    future = m.make_future_dataframe(periods=horizon)
    future['cap'] = 1.2 * merged_df['y'].max()

    #Adding feature values to future dataframe
    future = pd.merge(future,feature_df,how="left")

    #Update Future Timeframe with prediction weather data instead of historical weather data to prevent overfitting
    cols_to_update = ['temp', 'humidity', 'clouds', 'wind_speed', 'wind_deg', 'rain']
    future.loc[future.index[-(horizon):], cols_to_update] = weather_predict[cols_to_update].values

    #Predicting
    forecast = m.predict(future)
    #Clipping low predictions at 200€
    for col in ['yhat', 'yhat_lower', 'yhat_upper']:
        forecast[col] = forecast[col].clip(lower=200.0)

    seven_day_forecast = forecast.tail(horizon)
    seven_day_forecast_slim = seven_day_forecast[["ds","yhat_lower","yhat","yhat_upper"]]
    prediction_forecast = seven_day_forecast_slim
    prediction_forecast["y_true"] = y_test.head(horizon)
    prediction_forecast["error"]=abs(prediction_forecast["yhat"]-prediction_forecast["y_true"])

    return prediction_forecast
