from flask.views import MethodView
import json
import logging
import threading
from config.Config import getSystemConfig
from core.Algo import Algo
from utils.Utils import Utils


class StartAlgoAPI(MethodView):
    def post(self):
        # start algo in a separate thread
        if Utils.isMarketClosedForTheDay():
            return json.dumps({'error': "market closed"})
        x = threading.Thread(target=Algo.startAlgo)
        x.start()
        systemConfig = getSystemConfig()
        homeUrl = systemConfig['homeUrl'] + '?algoStarted=true'
        logging.info('Sending redirect url %s in response', homeUrl)
        respData = {'redirect': homeUrl}
        return json.dumps(respData)
