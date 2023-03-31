from prefect import task, Flow
import mlflow
from mlflow.tracking import MlflowClient
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import pandas as pd
import numpy as np
import datetime
from fbprophet import Prophet


@task
def load_data():
    # Load preprocessed data
    df = pd.read_csv("merged_data.csv")
    return df


@task
def split_data(df):
    # Set prediction date (input by user)
    prediction_date = pd.to_datetime("2023-08-01")

    # Split data into training and testing sets based on prediction date
    train_df = df[df["ds"] < prediction_date]
    test_df = df[df["ds"] >= prediction_date]

    X_train = train_df.drop(columns=["y"])
    y_train = train_df["y"]
    X_test = test_df.drop(columns=["y"])
    y_test = test_df["y"]
    
    return train_df, test_df


@task
def train_model(train_df):
    # Initialize the Prophet model
    m = Prophet()

    # Add relevant regressors
    m.add_regressor('weather_main')
    m.add_regressor('Holiday')
    m.add_regressor('inflation_rate')
    m.add_regressor('consumption_climate')
    m.add_regressor('cov_lock')
    m.add_regressor('unemp_Berlin_Mitte')
    m.add_regressor('unemp_Berlin_Mitte_Mitte')
    m.add_regressor('pedestrians')

    # Fit the Prophet model to the data
    m.fit(train_df)

    return m


@task
def test_model(model, test_df):
    # Make predictions on the test data
    future = model.make_future_dataframe(periods=7)
    forecast = model.predict(future)

# future df will need to add future data 


    # Calculate the mean absolute error of the predictions
    mae = mean_absolute_error(test_df['y'], forecast[-7:]['yhat'])

    return mae, forecast 



@task
def log_results(mae, model):
    # Set MLflow experiment and run ID
    experiment_name = "Fortune Frontier"
    mlflow.set_experiment(experiment_name)
    client = MlflowClient()
    experiment_id = client.get_experiment_by_name(experiment_name).experiment_id
    run_id = client.create_run(experiment_id).info.run_id
    
    # Log metrics
    mlflow.log_metric("mae", mae)
    
    # Log the model
    mlflow.pyfunc.log_model("model", python_model=model)
    
    # Print run ID
    print("MLflow run ID:", run_id)


with Flow("prophet-model") as flow:
    data = load_data()
    train, test = split_data(data)
    model = train_model(train)
    mae = test_model(model, test)
    log_results(mae, model)


flow.run()
