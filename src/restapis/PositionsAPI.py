from flask.views import MethodView
from flask import render_template
import json
import logging
from core.Controller import Controller


class PositionsAPI(MethodView):
    def get(self):
        brokerHandle = Controller.getBrokerLogin().getBrokerHandle()
        positions = brokerHandle.positions()
        logging.info('User positions => %s', positions)
        return render_template('record.html', records=positions['net'], colnames=['tradingsymbol', 'buy_quantity', 'buy_price', 'pnl'])
