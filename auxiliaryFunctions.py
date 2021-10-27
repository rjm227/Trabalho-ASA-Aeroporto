import math, bcrypt, random, time, createDb

#DONE time of each flight for future search for day, idea, distribution on the next 7 days

#Continuous probability exponential distribution where in 7 days there will be half the flights of today  HalfLife Decay Function in 7 days
def getFlightDay(randomFloat):  #randomFloat = [0,1)
    return 7 * math.log(randomFloat, 1/2)  #same as 1-randomFloat  2.526548489949

def getRandomDateFlight(): #Returns in seconds
    return 24*60*60*getFlightDay(random.random())

def encryptPassword(password):
    return bcrypt.hashpw(password.encode('UTF-8'), bcrypt.gensalt())

def comparePassword(password, hashedPassword):
    return bcrypt.checkpw(password.encode('UTF-8'), hashedPassword)

def checkSession(authString, ip, sessionLength, dbPath):
    if len(authString) > len("Bearer ") and authString[0:7] == "Bearer ":
        token = authString[7:]
        session = createDb.findSessionWithToken(token, dbPath)
        if session is not None and ip == session['ip']:
            currentTime = time.time()
            if currentTime <= session['expirationTime']:
                newExpirationTime = currentTime + sessionLength
                session['expirationTime'] = newExpirationTime  #Refreshing time of each session for each request 
                createDb.updateSessionExpirationTimeWithToken(token, newExpirationTime, dbPath)
                return session
            else:
                createDb.removeSessionByToken(token) 
                raise RuntimeError("Session Expired, please login again")
    raise RuntimeError("""Invalid Session, check if you're using the correct format "Bearer yourToken" and you're on the same IP or please login again""")