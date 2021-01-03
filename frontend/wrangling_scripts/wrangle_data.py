from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
import requests, datetime
import time
import numpy as np

endpoint = "http://127.0.0.1:8500"
days = 60
tickerSymbol='GLD'
scaler = MinMaxScaler()

def get_start_date(end_date, days):
    '''
    get the start date from end date
    '''
    #return end_date + relativedelta(bdays=-(days+10))
    return end_date - datetime.timedelta(days=(days+30))

def get_data(tickerSymbol, RATIO_TO_PREDICT = "mid"):
    '''
    Args:
        tickerSymbol (string) - ticker Symbol

    Returns:
        df (Dataframe) - raw data
    '''  
    #get data on this ticker
    tickerData = yf.Ticker(tickerSymbol)

    #get the historical prices for this ticker
    end_date = datetime.date.today()
    start_date = get_start_date(end_date, days)
    df = tickerData.history(period='1d', start=start_date, end=end_date)
    df['Mid'] = (df['Low']+df['High'])/2.0
    df.drop(columns=['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits'], inplace=True)
    return df

def preprocess_input_data(df):
    df = df.tail(days)
    scaler.fit(df.values.tolist())
    df = scaler.transform(df.values.tolist()) 
    return df.tolist()

def get_preds(df):
    data = preprocess_input_data(df)
    json_data = {"model_name": "default", "data": {"keys": [data]} }
    result = requests.post(endpoint, json=json_data)
    pred_output = result.json()['keys_output']
    rescaled_pred_output = scaler.inverse_transform(pred_output)[0][0]
    return rescaled_pred_output

def return_figures():
    """Creates plotly visualizations

    Args:
        None

    Returns:
        list (dict): list containing the four plotly visualizations

    """
    df = get_data(tickerSymbol).tail(days)
    # first chart plots arable land from 1990 to 2015 in top 10 economies 
    # as a line chart
    graph_one = []
 
    x_val = df.index
    y_val = df.values[:,0]
    graph_one.append( 
          go.Scatter(
          x = x_val,
          y = y_val,
          mode = 'lines',
          name = 'Gold Price'
          )
    )
    x_pred = df.index[-1] + datetime.timedelta(1)
    y_pred = get_preds(df)
    df_pred = pd.DataFrame(dict(date=[x_pred],value=[y_pred]))
    
    graph_one.append( 
          go.Scatter(
          x = df_pred.date,
          y = df_pred.value, 
          mode = 'markers',
          marker_symbol="star",
          name = 'Gold Price Prediction'
          )
      )
    
    layout_one = dict(
              title = 'Gold price chart and price prediction for the next day',
                xaxis = dict(title = 'Day', autotick=True),
                yaxis = dict(title = 'Mid Price in EUR'),
                )
    
    # append all charts to the figures list
    figures = []
    figures.append(dict(data=graph_one, layout=layout_one))

    return figures
