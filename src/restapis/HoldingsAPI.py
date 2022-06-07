from flask.views import MethodView
from flask import render_template
import json
import logging
from core.Controller import Controller


class HoldingsAPI(MethodView):
    def get(self):
        brokerHandle = Controller.getBrokerLogin().getBrokerHandle()
        holdings = brokerHandle.holdings()
        logging.info('User holdings => %s', holdings)
        # return json.dumps(holdings)
        return render_template('record.html', records=holdings, colnames=['tradingsymbol', 'quantity', 'average_price', 'pnl'])
