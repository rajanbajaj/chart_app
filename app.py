from flask import Flask, render_template, request, jsonify
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from rajan_nse.CandleStickPatterns import CandleStickPatterns
from pandas import DataFrame

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

# @app.route('/plot', methods=['POST'])
# def plot():
#     stock_symbol = request.form['symbol']
#     candleStickPatterns = CandleStickPatterns()
#     data = candleStickPatterns.getHistoricalData(stock_symbol)
#     data = DataFrame(data['data'])
#     data = data.tail(70)  # Get the last 70 days of data
#     data.reset_index(inplace=True)

#     fig = make_subplots(rows=1, cols=1)
#     candlestick = go.Candlestick(x=data['Date'],
#                                  open=data['Open'],
#                                  high=data['High'],
#                                  low=data['Low'],
#                                  close=data['Close'])
    
#     fig.add_trace(candlestick)
#     fig.update_layout(title=f'Candlestick chart for {stock_symbol}',
#                       xaxis_title='Date',
#                       yaxis_title='Price')

#     graphJSON = fig.to_json()
#     return render_template('plot.html', graphJSON=graphJSON, stock_symbol=stock_symbol)

@app.route('/tick/<int:tick>', methods=['GET'])
def tick(tick):
    stock_symbol = request.args.get('symbol')
    candleStickPatterns = CandleStickPatterns()
    data = candleStickPatterns.getHistoricalData(stock_symbol)
    data = DataFrame(data['data'])
    data = data.tail(70)  # Get the last 70 days of data
    data.reset_index(inplace=True)
    data = data.reindex(index=data.index[::-1])

    if tick < len(data):
        tick_data = data.iloc[tick]
        return jsonify({
            'Date': tick_data['CH_TIMESTAMP'],
            'Open': tick_data['CH_OPENING_PRICE'],
            'High': tick_data['CH_TRADE_HIGH_PRICE'],
            'Low': tick_data['CH_TRADE_LOW_PRICE'],
            'Close': tick_data['CH_CLOSING_PRICE']
        })
    else:
        return jsonify({}), 404

@app.route('/plot', methods=['POST'])
def plot():
    stock_symbol = request.form['symbol']
    candleStickPatterns = CandleStickPatterns()
    data = candleStickPatterns.getHistoricalData(stock_symbol)
    data = DataFrame(data["data"])
    data = data.tail(70)  # Get the last 70 days of data
    data.reset_index(inplace=True)
    data = data.reindex(index=data.index[::-1])
    data = data.head(1)

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
    return render_template('plot.html', graphJSON=graphJSON,  stock_symbol=stock_symbol)

if __name__ == '__main__':
    app.run(debug=True)
