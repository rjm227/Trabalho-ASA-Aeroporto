import copy, secrets
from flask import Flask, request, jsonify
from auxiliaryFunctions import *
from createDb import *

def setRoutes(app, sessions, constants):
    sessionLength = constants['sessionLength']
    dbPath = constants['dbPath']

    @app.route('/', methods=["GET"])
    def index():
        return "<h1>Trabalho de ASA: Sistema Backend de uma empresa de passagens aéreas </h1>", 200

    @app.route("/login", methods=["POST"])
    def login():
        requestJson = request.json
        login = requestJson['login']
        password = requestJson['password']
        ip = request.remote_addr
        if comparePassword(password, findPasswordWithUsername(login, dbPath)):  #password == senhas[login]   senhas = {"RenatoJunio": "SenhaRenatoJunio!"}
            token = secrets.token_urlsafe(32)
            session = {
                "token": token,
                "username": login,
                "ip": ip,
                "expirationTime": time.time() + sessionLength
            }
            insertSession(session, dbPath)
            return jsonify({"token": token}), 200
        return "Usuário ou Senha inválidos", 401

    @app.route("/logout", methods=["POST"])
    def logout():
        token = request.headers['Authorization']
        session = None
        try:
            session = checkSession(token, request.remote_addr, sessionLength, dbPath)
        except RuntimeError as e:
            return str(e), 401
        removeSessionByToken(session['token'], dbPath)
        return "Logout realizado com sucesso", 200

    @app.route("/session", methods=["GET"])
    def session():
        try:
            checkSession(request.headers['Authorization'], request.remote_addr, sessionLength, dbPath)
        except RuntimeError as e:
            return str(e), 200
        return "A sessão atual ainda não expirou", 200

    @app.route("/getAirports", methods=["GET"])
    def getAirports():
        try:
            checkSession(request.headers['Authorization'], request.remote_addr, sessionLength, dbPath)
        except RuntimeError as e:
            return str(e), 401
        return jsonify(findAllAirports(dbPath)), 200  #Better than json.dumps() because it already changes the content type header to application/json

    @app.route("/getAirportsByOrigin/<int:originId>", methods=["GET"])
    def getAirportsByOrigin(originId):
        try:
            checkSession(request.headers['Authorization'], request.remote_addr, sessionLength, dbPath)
        except RuntimeError as e:
            return str(e), 401
        if findAirportWithId(originId, dbPath) is None:
            return "originId does not exist", 400
        return jsonify(findAllAirportsByOrigin(originId, dbPath)), 200

    @app.route("/getFlights", methods=["GET"])
    def getFlights():
        try:
            checkSession(request.headers['Authorization'], request.remote_addr, sessionLength, dbPath)
        except RuntimeError as e:
            return str(e), 401
        formattedTime = request.args.get('date', None)   #UTC -03 Formatted  3-11-2021
        inputTime = None
        if not (formattedTime is None):
            try:
                timeFormat = "%d-%m-%Y"
                localTime = time.strptime(formattedTime, timeFormat) #days: 3, month:11, year: 2021, hours:0, minutes:0, seconds:0 (UTC -3)
                try:
                    inputTime = time.mktime(localTime) # seconds since EPOCH, UTC+0  1635942537.3509085
                except Exception:
                    return "Invalid time value", 400
            except Exception:
                return "Invalid time format, it should be on format {}.".format(timeFormat), 400
        flights = []
        if inputTime is None:
            flights = findAllFlights(dbPath)
        else:
            flights = findFlightsOnDate(inputTime, dbPath)
        return jsonify(flights), 200

    @app.route("/searchFlights", methods=["GET"])
    def searchFlights():
        try:
            checkSession(request.headers['Authorization'], request.remote_addr, sessionLength, dbPath)
        except RuntimeError as e:
            return str(e), 401
        originAirportId = request.args.get('originAirportId', None)
        numberOfPassengers = request.args.get('numberOfPassengers', 1)
        flights = []
        if originAirportId != None :
            try:
                originAirportId = int(originAirportId)
            except:
                return "originAirportId should be an integer", 400
        try:
            numberOfPassengers = int(numberOfPassengers)
        except:
            return "numberOfPassengers should be an integer", 400
        if originAirportId == None:
            flights = findFlightsByNumberOfPassengers(numberOfPassengers,dbPath)
        else:
            if findAirportWithId(originAirportId, dbPath) is None:
                return "originAirportId does not exist", 400
            flights = findFlightsByNumberOfPassengersAndAirport(numberOfPassengers, originAirportId, dbPath)
        return jsonify(flights), 200

    @app.route("/buyReservation", methods=["POST"])
    def buyReservation():
        session = None
        try:
            session = checkSession(request.headers['Authorization'], request.remote_addr, sessionLength, dbPath)
        except RuntimeError as e:
            return str(e), 401

        numberOfPassengers = request.json.get('numberOfPassengers', None)
        if(numberOfPassengers == None):
            return "numberOfPassengers should not be empty", 400
        if not isinstance(numberOfPassengers, int):
            return "numberOfPassengers should be an integer", 400
        if(numberOfPassengers <= 0):
            return "numberOfPassengers should be greater than 0", 400

        flightId = request.json.get('flightId', None)
        if(flightId == None):
            return "flightId should not be empty", 400
        if not isinstance(flightId, int):
            return "flightId should be an integer", 400
        selectedFlight = findFlightWithId(flightId, dbPath)
        if(selectedFlight == None):
            return "flightId does not exist", 400
        if(numberOfPassengers > selectedFlight['currentSlots']):
            return "numberOfPassengers should be less or equal than the current slots", 400
        selectedFlight['currentSlots'] -= numberOfPassengers
        updateFlightCurrentSlots(selectedFlight['id'], selectedFlight['currentSlots'], dbPath)
        totalCost = numberOfPassengers * selectedFlight['value']
        reservation = {
            'flightId': selectedFlight['id'],
            'username': session['username'],
            'numberOfETickets': numberOfPassengers,
            'totalCost': totalCost
        }
        insertReservation(reservation, dbPath)
        return jsonify(reservation), 200