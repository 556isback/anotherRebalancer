
import logbot
import ccxt
from ccxt.base.decimal_to_precision import decimal_to_precision  # noqa F401
from ccxt.base.decimal_to_precision import TRUNCATE              # noqa F401
from ccxt.base.decimal_to_precision import DECIMAL_PLACES        # noqa F401
import numpy as np
import time
import pandas as pd
class Exchange:
    def __init__(self):
        api_key = ""                        # api key and secret for connecting crypto exchange
        secret_key = ""
        password = ""                       # some exchange require password
        exchange = 'binance'                # crypto exchange you want to connect
        self.exchange = getattr(ccxt, exchange)({
            'apiKey': api_key,
            'secret': secret_key,
            #'password': password,
        })
        self.coins=['BTC','ETH']                     #coins to include in your portfolio, please note that USDT is hard coded and used as base currency, don't add USDT in here
        self.reTry = 3                               #api max retry count
        self.threshold = 0.005                       #weighs diffs threshold to performe rebalance on

    def load_markets(self):
        self.exchange.load_markets()

    def fetchOhlcv(self):
        res = {}
        tem = 'binance'
        # Supported exchanges
        timeframe = '15m'
        # Check if the symbol is available on the Exchange
        exchange = getattr(ccxt, tem)()
        symbols = [sym+'/USDT' for sym in self.coins if sym!= 'USDT']
        for symbol in symbols:
            while True:
                try:
                    data = exchange.fetch_ohlcv(symbol, timeframe, None, 1000)
                    header = ["Timestamp", "open", "high", "low", "close", "volume"]
                    df = pd.DataFrame(data, columns=header)
                    df = df[["Timestamp", "open", "high", "low", "close", "volume"]]
                    break
                except:
                    time.sleep(1)
            for i in range(1):
                while True:
                    try:
                        since = df.Timestamp.values[0] - 1000 * 15 * 60 * 1000
                        data = exchange.fetch_ohlcv(symbol, timeframe, since, 1000)
                        header = ["Timestamp", "open", "high", "low", "close", "volume"]
                        df1 = pd.DataFrame(data, columns=header)
                        df1 = df1[["Timestamp", "open", "high", "low", "close", "volume"]]
                        df = pd.concat([df1, df]).reset_index(drop=True)
                        break
                    except:
                        time.sleep(1)
            df = df[["Timestamp", "open", "high", "low", "close", "volume"]]
            df['Timestamp'] = pd.to_datetime(df['Timestamp'] / 1000, unit="s")
            df["open"] = pd.to_numeric(df["open"])
            df["high"] = pd.to_numeric(df["high"])
            df["low"] = pd.to_numeric(df["low"])
            df["close"] = pd.to_numeric(df["close"])
            df["volume"] = pd.to_numeric(df["volume"])
            res[symbol.split('/')[0]] = df
        return res

    def balances(self):
        """
        you might need to modify this part of the code,
        cause every exchange has different format in returning account balance
        :return:
        """
        count = 0
        while count < self.reTry:
            try:
                data = self.exchange.fetch_balance()
                balances = {sym:0 for sym in self.coins}
                balances['USDT'] = 0
                for sym in balances:
                    if sym in data:
                        balances[sym] = data[sym]['free']
                return balances
            except Exception as e:
                count+=1
                time.sleep(3)
                error = str(e)
        logbot.logs(error)



    def pos(self, payload: dict):

        symbol = payload['symbol']+'/USDT'
        side = payload['side']
        size = float(payload['size'])

        size =self.exchange.amount_to_precision(symbol, size)#decimal_to_precision(str(size), TRUNCATE, self.precision[payload['symbol']]['amount'], DECIMAL_PLACES)

        type = 'market'
        count = 0
        while count < self.reTry:
            try:
                order = self.exchange.create_order(symbol, type, side, size)
                logbot.logs('>>> open order for : {}'.format(symbol))
                logbot.logs('size: ' + str(size)+ ' side: ' + str(side))
                return True
            except Exception as e:
                count += 1
                time.sleep(3)
                error = str(e)
        logbot.logs(error)