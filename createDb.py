import json, random, time, sqlite3
from auxiliaryFunctions import *

def createDb(dbPath):
    #Source: https://raw.githubusercontent.com/algolia/datasets/master/airports/airports.json
    print("Creating DB")
    airportsArr = []
    with open("airports.json", "r") as readFile:
        airportsArr = json.load(readFile)
    airports = {}
    for airport in airportsArr:
        airports[int(airport['objectID'])] = airport

    #TODO: Insert all information into an SQL database
    maxDestinationAirports = 10
    for airportId in airports:
        numberOfChoices = random.randint(0, maxDestinationAirports)
        choices = random.choices(list(airports.keys()), k=numberOfChoices)
        try:
            choices.remove(airportId)
        except ValueError:
            pass
        airports[airportId]['destinationAirports'] = choices

    flightIdCount = 1
    originAirportChance = 0.6   #percentage of origin airports that have flight scheduled
    destinationAirportChance = 0.8   #percentage of destination airports that have flight scheduled
    minValue = 100                    #flight price
    maxValue = 10000
    minSlots = 10   #Min Capacity
    maxSlots = 1000
    airportIds = list(airports.keys())
    for airportId in airportIds:
        airport = airports[airportId]
        if(random.random() <= originAirportChance):
            destinationAirports = airport['destinationAirports']   #list of ID's
            numberOfChoices = int(len(destinationAirports) * destinationAirportChance)
            choices = random.choices(destinationAirports, k=numberOfChoices)
            try:           #concern duplicated from connections
                choices.remove(airportId)
            except ValueError:
                pass
            flights = []
            for choiceId in choices:
                value = random.randint(minValue, maxValue)
                capacity = random.randint(minSlots, maxSlots)
                currentSlots = random.randint(0, capacity)
                flightTime = getRandomDateFlight() + time.time()
                timeFormat = "%a, %Y-%m-%d %H:%M:%S %z"
                creationTime = time.time()
                flightTimeFormatted = time.strftime(timeFormat,time.localtime(flightTime))
                timeCreatedFormatted = time.strftime(timeFormat,time.localtime(creationTime))
                flights.append({
                    'id': flightIdCount,
                    'origin': airportId,
                    'destination': choiceId,
                    'capacity': capacity,
                    'currentSlots': currentSlots,
                    'flightTime': flightTime,
                    'creationTime': creationTime,
                    'flightTimeFormatted': flightTimeFormatted,
                    'timeCreatedFormatted': timeCreatedFormatted,
                    'value': value
                })
                flightIdCount += 1
            airport['flights'] = flights
        else:
            airport['flights'] = []

    reservations = []

    passwords = {
        "RenatoJunio": encryptPassword("SenhaRenatoJunio!"),  #Visually Exposed for testing purposes (Dev enviroment)
        "Marcio": encryptPassword("SenhaMarcio&"),
        "Joao": encryptPassword("SenhaJoao%")
    }


    dbObject = {
        "airports": airports,
        "reservations": reservations,
        "passwords": passwords,
    }

    createSqliteDb(dbObject, dbPath)

def createSqliteDb(memoryDb, dbPath):
    connection = sqlite3.connect(dbPath)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS airports (
            id INTEGER PRIMARY KEY NOT NULL,
            name TEXT NOT NULL, 
            city TEXT, 
            country TEXT, 
            iata_code TEXT, 
            lat REAL, 
            lng REAL, 
            links_count INTEGER);""")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS connections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            origin_airport INTEGER NOT NULL,
            destination_airport INTEGER NOT NULL,
            FOREIGN KEY (origin_airport) REFERENCES airports (objectID),
            FOREIGN KEY (destination_airport) REFERENCES airports (objectID)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            origin INTEGER NOT NULL,
            destination INTEGER NOT NULL,
            capacity INTEGER NOT NULL,
            current_slots INTEGER NOT NULL,
            flight_time REAL NOT NULL,
            creation_time REAL NOT NULL,
            value REAL NOT NULL,
            FOREIGN KEY (origin) REFERENCES airports (objectID),
            FOREIGN KEY (destination) REFERENCES airports (objectID)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS passwords (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            ip TEXT NOT NULL,
            expiration_time REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservations(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            flight_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            number_of_e_tickets INTEGER NOT NULL,
            total_cost REAL NOT NULL,
            FOREIGN KEY (flight_id) REFERENCES flights (id),
            FOREIGN KEY (username) REFERENCES passwords (username)
        )
    """)
    
    connection.commit()
    connection.close()

    insertAirports(memoryDb['airports'], dbPath)
    insertConnections(memoryDb['airports'], dbPath)
    insertFlights(memoryDb['airports'], dbPath)
    insertPasswords(memoryDb['passwords'], dbPath)

def insertAll(tableName, sqlObjects, dbPath):
    if(len(sqlObjects) <= 0): return
    MAXIMUM_INSERT_SIZE = 100
    columnString = list(map(str,list(sqlObjects[0].keys())))
    repeatedQuestionMarks = []
    for i in range(len(columnString)):
        repeatedQuestionMarks.append("?") #",".join(["?","?","?","?"]) => "?,?,?,?"
    repeatedQuestionMarksString = "("+",".join(repeatedQuestionMarks)+")"
    repeatedQMSList = []

    connection = sqlite3.connect(dbPath)
    cursor = connection.cursor()
    i = 0
    values = []
    l = len(sqlObjects)
    for sqlObject in sqlObjects:
        values += list(map(str, list(sqlObject.values())))
        repeatedQMSList.append(repeatedQuestionMarksString)
        i+=1
        if i % MAXIMUM_INSERT_SIZE == 0 or i >= l:
            s = f"""INSERT INTO {tableName} ({",".join(columnString)}) VALUES {",".join(repeatedQMSList)};"""
            cursor.execute(s, tuple(values))
            values = []
            repeatedQMSList = []
    
    connection.commit()
    connection.close()

def insertAirports(airports, dbPath):
    sqlObjects = []
    for airportId in airports:
        airport = airports[airportId]
        sqlObjects.append({
            "id": airport['objectID'],
            "name": airport['name'],
            "city": airport["city"],
            "country": airport["country"],
            "iata_code": airport['iata_code'],
            "lat": airport['_geoloc']['lat'],
            "lng": airport['_geoloc']['lng'],
            "links_count": airport['links_count']
        })
    insertAll("airports", sqlObjects, dbPath)

def insertConnections(airports, dbPath):  #airports = {} dict
    sqlObjects = []
    for airportId in airports:
        airport = airports[airportId]
        destinationAirports = airport['destinationAirports']
        for destinationAirportId in destinationAirports:
            sqlObjects.append({
                "origin_airport": airportId, 
                "destination_airport": destinationAirportId
            })
    insertAll("connections", sqlObjects, dbPath)

def insertFlights(airports, dbPath):
    flights = []
    for airportId in airports:
        flights += airports[airportId]['flights']
    
    sqlObjects = []
    for flight in flights:
        sqlObjects.append({
            "origin": flight['origin'], 
            "destination": flight['destination'], 
            "capacity": flight['capacity'], 
            "current_slots": flight['currentSlots'], 
            "flight_time": flight['flightTime'], 
            "creation_time": flight['creationTime'], 
            "value": flight['value']
        })
    insertAll("flights", sqlObjects, dbPath)

def insertPasswords(passwords, dbPath):
    sqlObjects = []
    for username in passwords:
        sqlObjects.append({
            "username": username,
            "password": passwords[username].decode("utf-8")
        })
    insertAll("passwords", sqlObjects, dbPath)

def insertReservation(reservation, dbPath):
    connection = sqlite3.connect(dbPath)
    cursor = connection.cursor()

    cursor.execute("INSERT INTO reservations (flight_id, username, number_of_e_tickets, total_cost) VALUES (?,?,?,?)",(reservation['flightId'],reservation['username'],reservation['numberOfETickets'],reservation['totalCost']))

    connection.commit()
    connection.close()

def insertSession(session, dbPath):
    connection = sqlite3.connect(dbPath)
    cursor = connection.cursor()

    cursor.execute("INSERT INTO sessions (token, username, ip, expiration_time) VALUES (?,?,?,?)",(session['token'],session['username'],session['ip'],session['expirationTime']))

    connection.commit()
    connection.close()

def findSessionWithToken(token, dbPath):
    connection = sqlite3.connect(dbPath)
    cursor = connection.cursor()

    cursor.execute("SELECT token,username,ip,expiration_time FROM sessions WHERE token = ?",(token,))
    sessionArr = cursor.fetchone()
    connection.commit()
    connection.close()

    if sessionArr is None:
        return None

    session = {}
    session['token'],session['username'],session['ip'],session['expirationTime'] = sessionArr

    return session

def updateSessionExpirationTimeWithToken(token, expirationTime, dbPath):
    connection = sqlite3.connect(dbPath)
    cursor = connection.cursor()

    cursor.execute("UPDATE sessions SET expiration_time = ? WHERE token = ?",(expirationTime,token))

    connection.commit()
    connection.close()

def removeSessionByToken(token, dbPath):
    connection = sqlite3.connect(dbPath)
    cursor = connection.cursor()

    cursor.execute("DELETE FROM sessions WHERE token = ?",(token,))

    connection.commit()
    connection.close()

def findPasswordWithUsername(username, dbPath):
    connection = sqlite3.connect(dbPath)
    cursor = connection.cursor()

    cursor.execute("SELECT password FROM passwords WHERE username = ?",(username,))
    password = cursor.fetchone()[0]

    connection.commit()
    connection.close()
    
    return password.encode('utf8')

def findAllAirports(dbPath):
    connection = sqlite3.connect(dbPath)
    cursor = connection.cursor()

    cursor.execute("SELECT id,name,city,country,iata_code,lat,lng,links_count from airports")
    airportArr = cursor.fetchall()
    airports = []
    for airportValues in airportArr:
        airport = {}
        airport['_geoloc'] = {}
        airport['objectID'], airport['name'], airport["city"], airport["country"], airport['iata_code'], airport['_geoloc']['lat'], airport['_geoloc']['lng'], airport['links_count'] = airportValues
        airports.append(airport)
    
    connection.commit()
    connection.close()

    return airports

def findAirportWithId(id, dbPath):
    connection = sqlite3.connect(dbPath)
    cursor = connection.cursor()

    cursor.execute("SELECT * from airports WHERE id = ?", (id,))
    airportValues = cursor.fetchone()
    if airportValues == None:
        connection.commit()
        connection.close()
        return None

    airport = {}
    airport['_geoloc'] = {}
    airport['objectID'], airport['name'], airport["city"], airport["country"], airport['iata_code'], airport['_geoloc']['lat'], airport['_geoloc']['lng'], airport['links_count'] = airportValues

    connection.commit()
    connection.close()
    return airport

def findAllAirportsByOrigin(originId, dbPath):
    connection = sqlite3.connect(dbPath)
    cursor = connection.cursor()

    cursor.execute("SELECT a.* from connections c INNER JOIN airports a ON c.destination_airport = a.id WHERE c.origin_airport = ?", (originId,))
    airportArr = cursor.fetchall()
    airports = []
    for airportValues in airportArr:
        airport = {}
        airport['_geoloc'] = {}
        airport['objectID'], airport['name'], airport["city"], airport["country"], airport['iata_code'], airport['_geoloc']['lat'], airport['_geoloc']['lng'], airport['links_count'] = airportValues
        airports.append(airport)

    connection.commit()
    connection.close()

    return airports

def findAllFlights(dbPath):
    connection = sqlite3.connect(dbPath)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM flights")
    flightArr = cursor.fetchall()   #[(1,3682,106..),(2,3682,1553...),...] #Only row values,not column names
    flights = []
    for flightValues in flightArr:
        flight = {}
        flight['id'], flight['origin'], flight['destination'], flight['capacity'], flight['currentSlots'], flight['flightTime'], flight['creationTime'], flight['value'] = flightValues
        timeFormat = "%a, %Y-%m-%d %H:%M:%S %z"
        flight['flightTimeFormatted'] = time.strftime(timeFormat,time.localtime(flight['flightTime']))
        flight['creationTimeFormatted'] = time.strftime(timeFormat,time.localtime(flight['creationTime']))
        flights.append(flight)

    connection.commit()
    connection.close()
    return flights

def findFlightWithId(id, dbPath):
    connection = sqlite3.connect(dbPath)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM flights WHERE id = ?", (id,))
    flightValues = cursor.fetchone()
    if flightValues == None:
        connection.commit()
        connection.close()
        return None

    flight = {}
    flight['id'], flight['origin'], flight['destination'], flight['capacity'], flight['currentSlots'], flight['flightTime'], flight['creationTime'], flight['value'] = flightValues
    timeFormat = "%a, %Y-%m-%d %H:%M:%S %z"
    flight['flightTimeFormatted'] = time.strftime(timeFormat,time.localtime(flight['flightTime']))
    flight['creationTimeFormatted'] = time.strftime(timeFormat,time.localtime(flight['creationTime']))

    connection.commit()
    connection.close()
    return flight

def findFlightsOnDate(date, dbPath):  #Date in seconds since EPOCH on 00:00:00 UTC
    connection = sqlite3.connect(dbPath)
    cursor = connection.cursor()

    dateEnd = date + 24*60*60    #00:00:00 of the next day
    cursor.execute("SELECT * FROM flights WHERE flight_time >= ? AND flight_time < ?", (date, dateEnd))
    flightArr = cursor.fetchall()
    flights = []
    for flightValues in flightArr:
        flight = {}
        flight['id'], flight['origin'], flight['destination'], flight['capacity'], flight['currentSlots'], flight['flightTime'], flight['creationTime'], flight['value'] = flightValues
        timeFormat = "%a, %Y-%m-%d %H:%M:%S %z"
        flight['flightTimeFormatted'] = time.strftime(timeFormat,time.localtime(flight['flightTime']))
        flight['creationTimeFormatted'] = time.strftime(timeFormat,time.localtime(flight['creationTime']))
        flights.append(flight)

    connection.commit()
    connection.close()
    return flights

def findFlightsByNumberOfPassengers(numberOfPassengers, dbPath):
    connection = sqlite3.connect(dbPath)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM flights WHERE current_slots >= ? ORDER BY value ASC", (numberOfPassengers,))
    flightArr = cursor.fetchall()
    flights = []
    for flightValues in flightArr:
        flight = {}
        flight['id'], flight['origin'], flight['destination'], flight['capacity'], flight['currentSlots'], flight['flightTime'], flight['creationTime'], flight['value'] = flightValues
        timeFormat = "%a, %Y-%m-%d %H:%M:%S %z"
        flight['flightTimeFormatted'] = time.strftime(timeFormat,time.localtime(flight['flightTime']))
        flight['creationTimeFormatted'] = time.strftime(timeFormat,time.localtime(flight['creationTime']))
        flights.append(flight)

    connection.commit()
    connection.close()
    return flights

def findFlightsByNumberOfPassengersAndAirport(numberOfPassengers, airportId, dbPath):
    connection = sqlite3.connect(dbPath)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM flights WHERE current_slots >= ? AND origin = ? ORDER BY value ASC", (numberOfPassengers,airportId))
    flightArr = cursor.fetchall()
    flights = []
    for flightValues in flightArr:
        flight = {}
        flight['id'], flight['origin'], flight['destination'], flight['capacity'], flight['currentSlots'], flight['flightTime'], flight['creationTime'], flight['value'] = flightValues
        timeFormat = "%a, %Y-%m-%d %H:%M:%S %z"
        flight['flightTimeFormatted'] = time.strftime(timeFormat,time.localtime(flight['flightTime']))
        flight['creationTimeFormatted'] = time.strftime(timeFormat,time.localtime(flight['creationTime']))
        flights.append(flight)

    connection.commit()
    connection.close()
    return flights

def updateFlightCurrentSlots(flightId, newCurrentSlots, dbPath):
    connection = sqlite3.connect(dbPath)
    cursor = connection.cursor()

    cursor.execute("UPDATE flights SET current_slots = ? WHERE id = ?",(newCurrentSlots,flightId))

    connection.commit()
    connection.close()