# Description
This crypto trading bot is designed for rebalancing dynamic weights of crypto assets, allowing you to maintain a well-structured portfolio. The bot helps you automatically adjust the allocation of different cryptocurrencies based on market conditions, ensuring that your investment remains optimized.

## Usage

To get started, follow these steps:

Open the api.py file and fill in your API credentials for the desired crypto exchange. In some cases, a password might be required by the exchange.

```
api_key = ""                        # api key and secret for connecting crypto exchange
secret_key = ""
password = ""                       # some exchange require password
exchange = 'binance'                # crypto exchange you want to connect
```
Configure the settings to suit your needs:
```
self.coins=['BTC','ETH']                     #coins to include in your portfolio, please note that USDT is hard coded and used as base currency, don't add USDT in here
self.reTry = 3                               #api max retry count
self.threshold = 0.005                       #weighs diffs threshold to performe rebalance on
```

The next part requires some customization based on the return JSON format of the fetch_balance method in ccxt, which may vary depending on the exchange you trade on. Modify the following code in api.py as needed:

```
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
```

In rebalancer.py, the code already implements a simple calculation of the optimal weights using PyPortfolioOpt. However, please note that using this demonstration code alone may not guarantee optimal results in all market environments. Consider setting fixed weights for each asset if you already have a desired portfolio structure, like weights={'BTC':0.6,'ETH':0.4}.

```
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

```

Define the times for rebalancing and recalculating optimal weights in rebalancer.py. You can set up multiple times if needed.
```
"""
strategy optimize the weights and rebalance at local time 00:00
"""
iteratey()
schedule.every().day.at("00:00").do(iteratey)
```

If you would like to receive rebalance status notifications on Discord, you can fill in the webhook link in logbot.py.

With these configurations, your crypto trading bot is ready.

## disclaimer
This software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software.

The creator of this project is not responsible for any losses that users may encounter while using this software.
