from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
import requests, datetime
import time
import numpy as np

endpoint = "http://127.0.0.1:8500"
tickerSymbol = 'GC=F' # prediction asset
pred_col = 'Close' # prediction column
input_len = 60 # length of input sequence
output_len = 60 # length into future to predict
scaler = MinMaxScaler()


def get_start_date(end_date, input_len):
    '''
    get the start date from end date
    '''
    return end_date - datetime.timedelta(days=(input_len+40))

def get_data(tickerSymbol):
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
    start_date = get_start_date(end_date, input_len)
    df = tickerData.history(period='1d', start=start_date, end=end_date)
    df.drop(columns=['Dividends', 'Stock Splits'], inplace=True)
    return df.tail(input_len)

def preprocess_input_data(df):
    df[pred_col] = scaler.fit_transform(df[pred_col].values.reshape(-1,1))
    return df.values.tolist()

def get_preds(df):
    data = preprocess_input_data(df)
    json_data = {"data": {"input": [data]}}
    result = requests.post(endpoint, json=json_data)
    output = np.array(result.json()['output'][0]).reshape(-1,1)
    output = scaler.inverse_transform(output)
    return output.reshape(1,-1)

def return_figures():
    """Creates plotly visualizations

    Args:
        None

    Returns:
        list (dict): list containing the four plotly visualizations

    """
    df = get_data(tickerSymbol)
    # Gold chart plot
    # as a line chart
    graph_one = []
 
    x_val = df.index
    y_val = df[pred_col].values
    graph_one.append( 
          go.Scatter(
          x = x_val,
          y = y_val,
          mode = 'lines',
          name = 'Gold Price'
          )
    )
    x_preds = pd.date_range(datetime.datetime.today().date(), periods=output_len, freq='D')
    y_preds = get_preds(df)[0]
    
    # Gold price action prediction 
    # as a line chart   
    graph_one.append( 
          go.Scatter(
          x = x_preds,
          y = y_preds, 
          mode = 'lines',
          name = 'Gold Price Prediction'
          )
      )
    
    layout_one = dict(
              title = 'Gold price chart and price prediction for the next day',
                xaxis = dict(title = 'Day', autotick=True),
                yaxis = dict(title = 'Gold Price in Dollar'),
                )
    
    # append all charts to the figures list
    figures = []
    figures.append(dict(data=graph_one, layout=layout_one))

    return figures
