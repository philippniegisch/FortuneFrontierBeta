import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from prophet import Prophet
from .preprocess import preprocess_revenue

def baseline_model():

    #Model
    model = Prophet()

    #Load Data
    df = preprocess_revenue()

    #Prediction Date
    split_date = "2022-07-31"

    #Splitting the data
    split_date = "2022-07-31"
    index_split = df[df["ds"]==split_date].index[0]+1
    df_train = df.iloc[:index_split]
    df_test = df.iloc[index_split:]
    y_test = pd.DataFrame(df_test["y"])

    #Fitting the model
    m = Prophet()
    m = m.fit(df_train)

    #Creating future dataframe
    future = m.make_future_dataframe(periods=7)

    #Predicting
    forecast = m.predict(future)
    seven_day_forecast = forecast.tail(7)
    seven_day_forecast_slim = seven_day_forecast[["ds","yhat_lower","yhat","yhat_upper"]]
    prediction_forecast = seven_day_forecast_slim
    prediction_forecast["y_true"] = y_test.head(7)
    prediction_forecast["error"]=abs(prediction_forecast["yhat"]-prediction_forecast["y_true"])

    return prediction_forecast
