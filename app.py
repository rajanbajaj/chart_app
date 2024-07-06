from flask import Flask, render_template, request
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from rajan_nse.CandleStickPatterns import CandleStickPatterns
from pandas import DataFrame

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/plot', methods=['POST'])
def plot():
    stock_symbol = request.form['symbol']
    candleStickPatterns = CandleStickPatterns()
    data = candleStickPatterns.getHistoricalData(stock_symbol)
    data = DataFrame(data["data"])

    fig = make_subplots(rows=1, cols=1)
    candlestick = go.Candlestick(x=data['CH_TIMESTAMP'],
                                 open=data['CH_OPENING_PRICE'],
                                 high=data['CH_TRADE_HIGH_PRICE'],
                                 low=data['CH_TRADE_LOW_PRICE'],
                                 close=data['CH_CLOSING_PRICE'])
    
    fig.add_trace(candlestick)
    fig.update_layout(title=f'Candlestick chart for {stock_symbol}',
                      xaxis_title='Date',
                      yaxis_title='Price')
    
    graphJSON = fig.to_json()
    return render_template('plot.html', graphJSON=graphJSON)

if __name__ == '__main__':
    app.run(debug=True)
