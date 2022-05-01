import logging
from bs4 import BeautifulSoup
import pandas as pd
import requests

from models.Direction import Direction
from models.ProductType import ProductType
from strategies.BaseStrategy import BaseStrategy
from utils.Utils import Utils
from trademgmt.Trade import Trade
from trademgmt.TradeManager import TradeManager

# Each strategy has to be derived from BaseStrategy


class SampleStrategy(BaseStrategy):
    __instance = None

    @staticmethod
    def getInstance():  # singleton class
        if SampleStrategy.__instance == None:
            SampleStrategy()
        return SampleStrategy.__instance

    def __init__(self):
        if SampleStrategy.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            SampleStrategy.__instance = self
        # Call Base class constructor
        super().__init__("MORNING STAR")
        # Initialize all the properties specific to this strategy
        self.URL = 'https://chartink.com/screener/morning-star-candlestick-pattern'
        self.productType = ProductType.MIS
        self.driver.get(self.URL)
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        self.temp_stock_list = []
        for stocks in soup.find_all('table', class_='table table-striped scan_results_table dataTable no-footer')[0].tbody.find_all('tr'):
            self.temp_stock_list.append(stocks.find_all('td')[2].text)
        self.symbols = list(set(self.temp_stock_list)
                            & set(self.nifty500_list))

        self.slPercentage = 2
        self.targetPercentage = 2
        # When to start the strategy. Default is Market start time
        self.startTimestamp = Utils.getTimeOfToDay(9, 30, 0)
        # This is not square off timestamp. This is the timestamp after which no new trades will be placed under this strategy but existing trades continue to be active.
        self.stopTimestamp = Utils.getTimeOfToDay(14, 30, 0)
        self.squareOffTimestamp = Utils.getTimeOfToDay(
            15, 0, 0)  # Square off time
        # Capital to trade (This is the margin you allocate from your broker account for this strategy)
        self.capital = 1000
        self.leverage = 2  # 2x, 3x Etc
        self.maxTradesPerDay = 3  # Max number of trades per day under this strategy
        self.isFnO = False  # Does this strategy trade in FnO or not
        # Applicable if isFnO is True (1 set means 1CE/1PE or 2CE/2PE etc based on your strategy logic)
        self.capitalPerSet = 0

    def process(self):
        if len(self.trades) >= self.maxTradesPerDay:
            return
        # This is a strategy with the following logic:
        # 1. Bullish reversal pattern in which a stock which had a long white body a 2 days ago,  then opened lower with a Doji a day ago and finally closed above the previous day
        for symbol in self.symbols:
            quote = self.getQuote(symbol)
            if quote == None:
                logging.error('%s: Could not get quote for %s',
                              self.getName(), symbol)
                continue

            cmp = quote.lastTradedPrice
            logging.info('%s: %s => CMP = %f', self.getName(
            ), symbol, cmp)

            direction = 'LONG'
            breakoutPrice = 0

            if direction == None:
                continue

            self.generateTrade(symbol, direction, breakoutPrice, cmp)

    def generateTrade(self, tradingSymbol, direction, breakoutPrice, cmp):
        trade = Trade(tradingSymbol)
        trade.strategy = self.getName()
        trade.direction = direction
        trade.productType = self.productType
        trade.placeMarketOrder = True
        trade.requestedEntry = breakoutPrice
        # setting this to strategy timestamp
        trade.timestamp = Utils.getEpoch(self.startTimestamp)
        trade.qty = int(self.calculateCapitalPerTrade() / breakoutPrice)
        if trade.qty == 0:
            trade.qty = 1  # Keep min 1 qty
        if direction == 'LONG':
            trade.stopLoss = Utils.roundToNSEPrice(
                breakoutPrice - breakoutPrice * self.slPercentage / 100)
            if cmp < trade.stopLoss:
                trade.stopLoss = Utils.roundToNSEPrice(cmp - cmp * 1 / 100)
        else:
            trade.stopLoss = Utils.roundToNSEPrice(
                breakoutPrice + breakoutPrice * self.slPercentage / 100)
            if cmp > trade.stopLoss:
                trade.stopLoss = Utils.roundToNSEPrice(cmp + cmp * 1 / 100)

        if direction == 'LONG':
            trade.target = Utils.roundToNSEPrice(
                breakoutPrice + breakoutPrice * self.targetPercentage / 100)
        else:
            trade.target = Utils.roundToNSEPrice(
                breakoutPrice - breakoutPrice * self.targetPercentage / 100)

        trade.intradaySquareOffTimestamp = Utils.getEpoch(
            self.squareOffTimestamp)
        # Hand over the trade to TradeManager
        TradeManager.addNewTrade(trade)

    def shouldPlaceTrade(self, trade, tick):
        # First call base class implementation and if it returns True then only proceed
        if super().shouldPlaceTrade(trade, tick) == False:
            return False

        if tick == None:
            return False

        if trade.direction == Direction.LONG and tick.lastTradedPrice > trade.requestedEntry:
            return True
        elif trade.direction == Direction.SHORT and tick.lastTradedPrice < trade.requestedEntry:
            return True
        return False