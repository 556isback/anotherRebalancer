
from api import Exchange
import pandas as pd
import logbot
import warnings
import schedule
import time
from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import CovarianceShrinkage
from pypfopt.efficient_frontier import EfficientFrontier
warnings.filterwarnings("ignore")




def calpair():
    time.sleep(2)
    exchange_api = Exchange()
    exchange_api.load_markets()
    while True:
        try:
            data3 = exchange_api.fetchOhlcv()
            break
        except:
            time.sleep(5)
    tempdata = pd.DataFrame()
    for sym in data3:
        tempdata[sym] = data3[sym].close.values
    """
    This is the part where you can modify how optimized weights are calculated
    For demonstration here is the code using 
    PyPortfolioOpt(https://github.com/robertmartin8/PyPortfolioOpt) EfficientFrontier.min_volality() method to optimize the weights
    """

    mu = mean_historical_return(tempdata)
    S = CovarianceShrinkage(tempdata).ledoit_wolf()

    ef = EfficientFrontier(mu, S)
    weights = ef.min_volality()  #
    weights['USDT'] = 1 - sum([weights[sym] for sym in weights])

    '''
    strategy modification ends here
    '''

    logbot.logs(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))

    return weights, data3, exchange_api

def manager(weights, data3, exchange_api):

    logbot.logs('weights: '+str(weights))
    time.sleep(1)
    bal = exchange_api.balances()
    price = {sym: data3[sym]['close'].values[1] for sym in data3}
    price['USDT'] = 1
    bal = {sym:bal[sym]*price[sym] for sym in bal}
    logbot.logs('position in USDT: '+str(bal))
    cro = 0
    for sym in bal:
        if sym!='USDT':
            cro+=bal[sym]
    fcro = sum([bal[i] for i in bal])
    logbot.logs('>>> totoal position in USDT ' + str(round(cro,2)))
    logbot.logs('>>> totoal position used ' + str(round(cro / fcro*100,2))+'%')
    
    diffs = {}
    for sym in bal:
        if sym != 'USDT':
            perc = bal[sym] / fcro
            diffs[sym] = weights[sym] - perc

    diffs = {k: v  for k, v in sorted(diffs.items(), key=lambda item: item[1])}

    for sym in diffs:
        diffU = diffs[sym] * fcro
        if diffU > 5 and diffs[sym] > exchange_api.threshold:
            size = diffU / price[sym]
            if exchange_api.pos({'symbol': sym, 'size': size, 'side': 'buy'}):
                logbot.logs('add fund for ' + sym + ' about ' + str(diffU) + 'USDT')
        if diffU < -5 and diffs[sym] < -exchange_api.threshold:
            size = abs(diffU) / price[sym]
            if exchange_api.pos({'symbol': sym, 'size': size, 'side': 'sell'}):
                logbot.logs('reduce fund for ' + sym + ' about ' + str(diffU) + 'USDT')

def iteratey():
    weights, data3, api = calpair()
    manager(weights, data3, api)
    logbot.logs(">>>  schedule task finish")
    return True

"""
strategy optimize the weights and rebalance at local time 00:00
"""
iteratey()
schedule.every().day.at("00:00").do(iteratey)

while True:
    schedule.run_pending()  # 运行所有可运行的任务
    time.sleep(1)
