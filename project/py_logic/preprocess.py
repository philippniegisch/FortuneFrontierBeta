#IMPORTS
import pandas as pd
import numpy as np
import datetime

def preprocess_revenue():
    #import raw revenue data
    df_2016 = pd.read_csv("raw_data/orders2016.csv", sep=";")
    df_2017 = pd.read_csv("raw_data/orders2017.csv", sep=";")
    df_2018 = pd.read_csv("raw_data/orders2018.csv", sep=";")
    df_2019 = pd.read_csv("raw_data/orders2019.csv", sep=";")
    df_2020 = pd.read_csv("raw_data/orders2020.csv", sep=";")
    df_2021 = pd.read_csv("raw_data/orders2021.csv", sep=";")
    df_2022 = pd.read_csv("raw_data/orders2022.csv", sep=";")

    df_list = [df_2016, df_2017, df_2018, df_2019, df_2020, df_2021, df_2022]

    #Dropping unnecessary columns, grouping by "date", summing "item_price" to get daily revenues

    for i, df in enumerate(df_list):
        df_list[i] = pd.DataFrame(df.groupby(by="date")["item_price"].sum()/100)

    #Concat all data in one dataframe, rename the columns for prophet

    df = pd.concat(df_list, ignore_index=False)
    df = df.rename(columns={"date": "ds", "item_price": "y"})
    df["ds"] = df.index
    df = df.reset_index(drop=True)
    df = df[["ds","y"]]

    #turning the ds (date) column into datetime

    df['ds']=pd.to_datetime(df['ds'])

    #Dropping outliers
    df = df[df["y"]>=60]
    df = df[df["y"]<=2300]
    df = df.reset_index(drop=True)

    return df

def preprocess_complete():

    #df data
    #import raw revenue data
    df_2016 = pd.read_csv("../../raw_data/orders2016.csv", sep=";")
    df_2017 = pd.read_csv("../../raw_data/orders2017.csv", sep=";")
    df_2018 = pd.read_csv("../../raw_data/orders2018.csv", sep=";")
    df_2019 = pd.read_csv("../../raw_data/orders2019.csv", sep=";")
    df_2020 = pd.read_csv("../../raw_data/orders2020.csv", sep=";")
    df_2021 = pd.read_csv("../../raw_data/orders2021.csv", sep=";")
    df_2022 = pd.read_csv("../../raw_data/orders2022.csv", sep=";")
    df_list = [df_2016, df_2017, df_2018, df_2019, df_2020, df_2021, df_2022]
    #Dropping unnecessary columns, grouping by "date", summing "item_price" to get daily revenues
    for i, df in enumerate(df_list):
        df_list[i] = pd.DataFrame(df.groupby(by="date")["item_price"].sum()/100)
    #Concat all data in one dataframe, rename the columns for prophet
    df = pd.concat(df_list, ignore_index=False)
    df = df.rename(columns={"date": "ds", "item_price": "y"})
    df["ds"] = df.index
    df = df.reset_index(drop=True)
    df = df[["ds","y"]]
    #turning the ds (date) column into datetim
    df['ds']=pd.to_datetime(df['ds'])
    #Dropping outliers
    df = df[df["y"]>=60]
    df = df[df["y"]<=2300]
    df = df.reset_index(drop=True)
    #remove the duplicates
    duplicates = df['ds'].duplicated()

    #weather data
    weather_df = pd.read_csv("../../feature_data/weather.csv")
    #drop some columns
    weather_df = weather_df.drop(columns=["dt","timezone","city_name","lat","lon","sea_level","grnd_level","weather_icon","rain_3h","snow_3h"])
    #rename
    weather_df = weather_df.rename(columns={"dt_iso":"ds","rain_1h":"rain","clouds_all":"clouds"})
    # convert the timestamp column to a datetime object with timezone information
    weather_df['ds'] = weather_df['ds'].str[:19]
    weather_df["ds"] = pd.to_datetime(weather_df["ds"])
    # Filter the rows between 8 am and 10 pm
    df_filtered = weather_df[(weather_df['ds'].dt.hour >= 8) & (weather_df['ds'].dt.hour <= 22)]
    #replace the nan value with 0 in whole dataset
    df_filtered = df_filtered.fillna(0)

    #group by he rain by sum
    df_filtered['sum_rain'] = df_filtered.groupby(pd.Grouper(key='ds', freq='D'))['rain'].transform('sum')
    df_filtered
    # Drop all rows where the time component of 'column1' is not 12:00:00
    df_filtered = weather_df[weather_df['ds'].dt.time == pd.to_datetime('12:00:00').time()]
    # convert the timestamp column to a datetime object
    df_filtered['ds'] = pd.to_datetime(df_filtered['ds'])
    # remove the hour from the ds column
    df_filtered['ds'] = df_filtered['ds'].dt.normalize()
    # convert the ds column back to datetime format without hour
    df_filtered['ds'] = pd.to_datetime(df_filtered['ds']).dt.date
    df_filtered["ds"] = pd.to_datetime(df_filtered["ds"])
    #drop the drop_duplicates
    df_filtered = df_filtered.drop_duplicates()
    #merge sum weather data after sum rain with df
    merged_df = pd.merge(df, df_filtered, on='ds', how='left')
    #drop_duplicates
    merged_df.drop_duplicates(subset='ds', inplace=True)

    ##holiday
    df_holiday= pd.read_csv("../../feature_data/holidays.csv")
    df_holiday = df_holiday.reset_index()
    df_holiday.columns = df_holiday.iloc[0]
    # drop the first row, which is now redundant
    df_holiday = df_holiday.drop(0)
    df_holiday['ds'] = pd.to_datetime(df_holiday['ds'])
    df_holiday.info()
    #merge holiday to df
    merged_df_h = pd.merge(merged_df,df_holiday,on="ds",how="left")
    merged_df = merged_df_h

    ##inflation
    df_inflation_rate= pd.read_csv("../../feature_data/inflation_rate.csv")
    df_inflation_rate['ds'] = pd.to_datetime(df_inflation_rate['ds'])
    #merge inflation to df
    merged_df= pd.merge(merged_df, df_inflation_rate, how='left', left_on='ds', right_on='ds')

    ##consumption climate
    df_consumption_climate = pd.read_csv("../../feature_data/consumption_climate.csv")
    df_consumption_climate['ds'] = pd.to_datetime(df_consumption_climate['ds'])
    #merge
    merged_df = pd.merge(merged_df, df_consumption_climate,on="ds",how="left")

    #covid
    merged_df['cov_lock'] = ((merged_df['ds'] >= pd.to_datetime("2020-03-22")) & (merged_df['ds'] <= pd.to_datetime("2020-04-21"))) | ((merged_df['ds'] >= pd.to_datetime("2020-12-16")) & (merged_df['ds'] <= pd.to_datetime("2021-01-09"))) | ((merged_df['ds'] >= pd.to_datetime("2020-04-22")) & (merged_df['ds'] <= pd.to_datetime("2020-05-03"))) | ((merged_df['ds'] >= pd.to_datetime("2020-10-10")) & (merged_df['ds'] <= pd.to_datetime("2020-12-15"))) | ((merged_df['ds'] >= pd.to_datetime("2021-03-31")) & (merged_df['ds'] <= pd.to_datetime("2021-05-18"))) | ((merged_df['ds'] >= pd.to_datetime("2021-11-02")) & (merged_df['ds'] <= pd.to_datetime("2021-12-09")))
    merged_df['cov_lock'] = merged_df['cov_lock'].astype(int)

    #Berlin Unemployment Mitte and Mitte Mitte
    df_unemp_ber= pd.read_csv("../../feature_data/berlin_unemployment.csv", sep=";")
    # fom object to datetype
    df_unemp_ber['Date'] = pd.to_datetime(df_unemp_ber['Date'])
    df_unemp_ber[['unemp_Berlin_Mitte', 'unemp_Berlin_Mitte_Mitte']] = df_unemp_ber[['unemp_Berlin_Mitte', 'unemp_Berlin_Mitte_Mitte']].apply(lambda x: x.str.replace(',', '.'))
    df_unemp_ber = df_unemp_ber.astype({"unemp_Berlin_Mitte": float, "unemp_Berlin_Mitte_Mitte": float})
    df_unemp_ber[['unemp_Berlin_Mitte', 'unemp_Berlin_Mitte_Mitte']] = df_unemp_ber[['unemp_Berlin_Mitte', 'unemp_Berlin_Mitte_Mitte']].div(100)
    df_unemp_ber.set_index('Date', inplace=True)
    df_unemp_ber = df_unemp_ber.resample('D').ffill()
    merged_df = pd.merge(merged_df, df_unemp_ber, how='left', left_on='ds', right_on='Date')

    #Fill NaNs and strip whitespaces
    merged_df = merged_df.fillna(0)
    merged_df = merged_df.rename(columns=lambda x: x.strip())
    #Drop unnecessary columns based on correlation or co-correlation
    merged_df.drop(['visibility', 'dew_point', 'feels_like', 'temp_min', 'temp_max', 'pressure', 'wind_gust',
            'snow_1h', 'weather_id', 'weather_main', 'weather_description', 'unemp_Berlin_Mitte_Mitte'], axis=1, inplace=True)

    return merged_df
