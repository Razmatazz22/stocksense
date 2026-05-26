from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({'status': 'StockSense API running', 'version': '2.0'})

@app.route('/price/<ticker>')
def get_price(ticker):
    try:
        t = yf.Ticker(ticker)
        info = t.fast_info
        hist = t.history(period='2d')
        price = round(float(info.last_price), 2)
        prev  = float(hist['Close'].iloc[-2]) if len(hist) >= 2 else price
        chg   = round((price - prev) / prev * 100, 2)
        return jsonify({
            'ticker': ticker,
            'price':  price,
            'high52': round(float(info.year_high), 2),
            'low52':  round(float(info.year_low), 2),
            'volume': int(info.three_month_average_volume or 0),
            'chgPct': chg,
            'status': 'live'
        })
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'failed'}), 500

@app.route('/prices')
def get_prices_bulk():
    tickers_param = request.args.get('tickers', '')
    if not tickers_param:
        return jsonify({'error': 'No tickers provided'}), 400
    tickers = [t.strip() for t in tickers_param.split(',') if t.strip()]
    if len(tickers) > 15:
        return jsonify({'error': 'Max 15 tickers per request'}), 400
    results = {}
    for ticker in tickers:
        try:
            t    = yf.Ticker(ticker)
            info = t.fast_info
            hist = t.history(period='2d')
            price = round(float(info.last_price), 2)
            prev  = float(hist['Close'].iloc[-2]) if len(hist) >= 2 else price
            results[ticker] = {
                'price':  price,
                'high52': round(float(info.year_high), 2),
                'low52':  round(float(info.year_low), 2),
                'chgPct': round((price - prev) / prev * 100, 2),
                'status': 'live'
            }
        except Exception as e:
            results[ticker] = {'status': 'failed', 'error': str(e)}
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
