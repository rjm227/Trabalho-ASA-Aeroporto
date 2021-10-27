from flask import Flask
from createDb import createDb
from routes import setRoutes
from pathlib import Path

def getConstants():
    return {
        #Session Config
        'sessionLength': 60*60,  #minutes * 60 = number of seconds of each session
        #Airport Connections Creation
        'maxDestinationAirports': 10,
        #Flight creation Configuration
        'originAirportChance': 0.6,
        'destinationAirportChance' : 0.8,
        'minValue' : 100,    #Value of tickets per person
        'maxValue' : 10000,
        'minSlots' : 10,     #Flight capacity
        'maxSlots' : 1000,
        'dbPath': "db/airports.db"
    }

def main():
    constants = getConstants()
    sessions = {}
    dbPath = constants['dbPath']
    my_file = Path(dbPath)
    if not my_file.is_file():
        createDb(dbPath)
    app = Flask(__name__)
    setRoutes(app, sessions, constants)
    app.run(host='0.0.0.0')
    return

if(__name__ == '__main__'):
    main()


