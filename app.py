from flask import Flask, render_template, request, jsonify
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from rajan_nse.CandleStickPatterns import CandleStickPatterns
from pandas import DataFrame
import pandas as pd
from datetime import date, timedelta


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/tick/<int:tick>', methods=['GET'])
def tick(tick):
    data = pd.read_csv('data.csv')

    if tick < len(data):
        tick_data = data.iloc[tick]
        return jsonify({
            'Date': tick_data['CH_TIMESTAMP'],
            'Open': tick_data['CH_OPENING_PRICE'],
            'High': tick_data['CH_TRADE_HIGH_PRICE'],
            'Low': tick_data['CH_TRADE_LOW_PRICE'],
            'Close': tick_data['CH_CLOSING_PRICE'],
            'Volume': float(tick_data['CH_TOT_TRADED_QTY'])
        })
    else:
        return jsonify({}), 404

@app.route('/plot', methods=['POST'])
def plot():
    stock_symbol = request.form['symbol']
    candleStickPatterns = CandleStickPatterns()
    
    # get latest 70 days data
    data = candleStickPatterns.getHistoricalData(stock_symbol)
    data = DataFrame(data["data"])

    #  reverse and save data
    data = data.tail(70)  # Get the last 70 days of data
    data.reset_index(inplace=True)
    data = data.reindex(index=data.index[::-1])
    data.to_csv('data.csv')

    # Find the complete date range
    # Identify missing dates
    full_date_range = pd.date_range(start=data['CH_TIMESTAMP'].min(), end=data['CH_TIMESTAMP'].max())
    missing_dates1 = full_date_range.difference(data['CH_TIMESTAMP'])

    # get previous 70 days data
    to_date = date.today() - timedelta(days=100)
    data = candleStickPatterns.getHistoricalData(stock_symbol, to_date)
    data = DataFrame(data["data"])

    # Find the complete date range
    # Identify missing dates
    full_date_range = pd.date_range(start=data['CH_TIMESTAMP'].min(), end=data['CH_TIMESTAMP'].max())
    missing_dates2 = full_date_range.difference(data['CH_TIMESTAMP'])

    missing_dates = missing_dates1.union(missing_dates2)

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                    row_heights=[0.6, 0.4], vertical_spacing=0.02)

    candlestick = go.Candlestick(
        x=data['CH_TIMESTAMP'],
        open=data['CH_OPENING_PRICE'],
        high=data['CH_TRADE_HIGH_PRICE'],
        low=data['CH_TRADE_LOW_PRICE'],
        close=data['CH_CLOSING_PRICE']
    )
    
    bar = go.Bar(
        x=data['CH_TIMESTAMP'],
        y=data['CH_TOT_TRADED_QTY'], 
        name='Volume'
    )

    fig.add_trace(candlestick, row=1, col=1)
    fig.add_trace(bar, row=2, col=1)
    fig.update_xaxes(rangebreaks=[dict(values=missing_dates)])
    fig.update_layout(
        title=f'Candlestick chart for {stock_symbol}',
        xaxis2_title='Date',
        yaxis_title='Price',
        yaxis2_title='Volume',
        height=500,  # Adjust height as needed
        xaxis_rangeslider_visible=False
    )
    
    graphJSON = fig.to_json()
    return render_template('plot.html', graphJSON=graphJSON,  stock_symbol=stock_symbol)

if __name__ == '__main__':
    app.run(debug=True)
