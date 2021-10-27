--Database File: airports.db
--Database Engine: sqLite

CREATE TABLE IF NOT EXISTS airports (
            id INTEGER PRIMARY KEY NOT NULL,
            name TEXT NOT NULL, 
            city TEXT, 
            country TEXT, 
            iata_code TEXT, 
            lat REAL, 
            lng REAL, 
            links_count INTEGER);

CREATE TABLE IF NOT EXISTS connections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            origin_airport INTEGER NOT NULL,
            destination_airport INTEGER NOT NULL,
            FOREIGN KEY (origin_airport) REFERENCES airports (objectID),
            FOREIGN KEY (destination_airport) REFERENCES airports (objectID)
        )

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

CREATE TABLE IF NOT EXISTS passwords (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )

CREATE TABLE IF NOT EXISTS reservations(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            flight_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            number_of_e_tickets INTEGER NOT NULL,
            total_cost REAL NOT NULL,
            FOREIGN KEY (flight_id) REFERENCES flights (id),
            FOREIGN KEY (username) REFERENCES passwords (username)
        )