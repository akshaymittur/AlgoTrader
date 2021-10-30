import json
import os

dir = os.path.dirname(__file__)
serverFile = os.path.join(dir, '../../config/server.json')
systemFile = os.path.join(dir, '../../config/system.json')
brokerFile = os.path.join(dir, '../../config/brokerapp.json')
holidayFile = os.path.join(dir, '../../config/holidays.json')


def getServerConfig():
    with open(serverFile, 'r') as server:
        jsonServerData = json.load(server)
        return jsonServerData


def getSystemConfig():
    with open(systemFile, 'r') as system:
        jsonSystemData = json.load(system)
        return jsonSystemData


def getBrokerAppConfig():
    with open(brokerFile, 'r') as brokerapp:
        jsonUserData = json.load(brokerapp)
        return jsonUserData


def getHolidays():
    with open(holidayFile, 'r') as holidays:
        holidaysData = json.load(holidays)
        return holidaysData


def getTimestampsData():
    serverConfig = getServerConfig()
    timestampsFilePath = os.path.join(
        serverConfig['deployDir'], 'timestamps.json')
    if os.path.exists(timestampsFilePath) == False:
        return {}
    timestampsFile = open(timestampsFilePath, 'r')
    timestamps = json.loads(timestampsFile.read())
    return timestamps


def saveTimestampsData(timestamps={}):
    serverConfig = getServerConfig()
    timestampsFilePath = os.path.join(
        serverConfig['deployDir'], 'timestamps.json')
    with open(timestampsFilePath, 'w') as timestampsFile:
        json.dump(timestamps, timestampsFile, indent=2)
    print("saved timestamps data to file " + timestampsFilePath)
