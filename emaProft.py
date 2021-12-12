#Import required libs
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import sys


#Setup colors for printing
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


#Check if args exist and if they do set values
if len(sys.argv) >= 2:
    try:
        startAmmount = float(sys.argv[1])
    except ValueError:
        startAmmount = 10000
else:
    startAmmount = 10000
if len(sys.argv) >= 3:
    try:
        smallEMA = int(sys.argv[2])
    except ValueError:
        smallEMA = 12
else:
    smallEMA = 12
if len(sys.argv) >= 4:
    try:
        largerEMA = int(sys.argv[3])
    except ValueError:
        largerEMA = 25
else:
    largerEMA = 25

if len(sys.argv) >= 5:
    startDate = sys.argv[4]
else:
    startDate = "2020-12-12"

if len(sys.argv ) >= 6:
    endDate = sys.argv[5]
else:
    endDate = "2021-12-12"

if len(sys.argv ) >= 7:
    ticker = sys.argv[6] 
else:
    ticker = "ETH"

#Download Price Data
cryptoPriceData = yf.download(ticker+"-USD",  start=startDate, end=endDate);

#Print Usage
print(f"\n{bcolors.WARNING} Usage: emaProft.py (Start Balence) (Small EMA) (Large EMA) (Start Date YYYY-MM-DD) (End Date YYYY-MM-DD) (Crypto EG. {ticker}){bcolors.ENDC}")

#Print Start Info
print(f"\n{bcolors.WARNING} Start Balence: {startAmmount} Small EMA: {smallEMA} Large EMA: {largerEMA} Start Date: {startDate} End Date: {endDate} {bcolors.ENDC}")

#Calc 2 EMAs
cryptoPriceData['smallerEMA'] = cryptoPriceData['Close'].ewm(span=smallEMA, adjust=False).mean()
cryptoPriceData['largerEMA'] = cryptoPriceData['Close'].ewm(span=largerEMA, adjust=False).mean()

#Init bals
usdBal = startAmmount
cryptoBal = 0

#Setup bool to store higher EMA
LargeEMAhigher = True;

print(f"\n{bcolors.WARNING} #########################EMA Data######################### {bcolors.ENDC}")
for index, row in cryptoPriceData.iterrows():
    #Check if EMA has flipped
    if row['largerEMA'] > row['smallerEMA'] and LargeEMAhigher == False:
        #Calc sale
        currentPrice = round(row["Close"],2)
        print(f"{bcolors.FAIL} Sell {round(cryptoBal, 2)} {ticker} @ {currentPrice} for {round(currentPrice * cryptoBal, 2)} USD, Profit: {round((currentPrice * cryptoBal) - startAmmount)} {bcolors.ENDC}")
        usdBal = cryptoBal * row["Close"]
        cryptoBal = 0
        LargeEMAhigher = True
    elif row['largerEMA'] < row['smallerEMA'] and LargeEMAhigher == True:
        #Calc buy
        currentPrice = round(row["Close"], 2)
        print(f"{bcolors.OKGREEN} Buy {round(usdBal)} USD of {ticker} @ {currentPrice} for {round(usdBal / currentPrice, 2)} {ticker} {bcolors.ENDC}")
        cryptoBal = usdBal / row["Close"]
        usdBal = 0
        LargeEMAhigher = False

#If any crypto left, sell
if LargeEMAhigher == False:
        usdBal = cryptoBal * cryptoPriceData["Close"].iget(-1)
        cryptoBal = 0
        LargeEMAhigher = True
        profit.append(usdBal - startAmmount)
        print(f"{bcolors.FAIL} Selling Remaining Crypto! {bcolors.ENDC}")

print(f"\n{bcolors.WARNING} #########################Market Data######################### {bcolors.ENDC}")

#Calc what would have been made in profit
MarketBal = startAmmount / cryptoPriceData.iloc[0]['Close']
MarketProfit = MarketBal * cryptoPriceData.iloc[-1]['Close']

#Get first and last price for printing
openPrice = cryptoPriceData.iloc[0]['Close']
closePrice = cryptoPriceData.iloc[-1]['Close']

#Print Market Data
print(f"{bcolors.OKGREEN} Buy {startAmmount} USD of {ticker} @ {round(openPrice, 2)} for {round(MarketBal)} {ticker} {bcolors.ENDC}")
print(f"{bcolors.FAIL} Sell {round(MarketBal)} {ticker} @ {round(closePrice, 2)} for {round(MarketProfit)} USD {bcolors.ENDC}")

#Print P/L
print(f"\n{bcolors.OKBLUE} USD balence: {round(usdBal, 2)}, Profit {round(usdBal - startAmmount, 2)}, Market Profit: {round( MarketProfit - startAmmount ,2)} {bcolors.ENDC}")

#Calc percent diff
percentDiff = (abs((MarketProfit- startAmmount) - (usdBal - startAmmount)) / (((MarketProfit- startAmmount) + (usdBal - startAmmount)) / 2)) * 100

#Calc if EMA or hodl has better oods
if MarketProfit > (usdBal - startAmmount):
    print(f"{bcolors.OKBLUE}{bcolors.BOLD} Market outperformed EMA strat by ${round(MarketProfit - (usdBal - startAmmount), 2)} ({round(percentDiff, 2)}%) {bcolors.ENDC}")
else:
    print(f"{bcolors.OKBLUE}{bcolors.BOLD} EMA outperformed Market strat by ${round((usdBal - startAmmount) - MarketProfit, 2) } ({round(percentDiff, 2)}%) {bcolors.ENDC}")
