# Import the sqlite3 module for working with SQLite databases
import sqlite3 
# Import the random module for generating random driver assignment
import random  

# Define the Driver class
class Driver:
    def __init__(self, id, name):
        self.id = id
        self.name = name

# Define the Rider class
class Rider:
    def __init__(self, id, name):
        self.id = id
        self.name = name

# Define the Ride class
class Ride:
    def __init__(self, id, rider_id, driver_id, distance, fare=None, status='Pending'):
        self.id = id
        self.rider_id = rider_id
        self.driver_id = driver_id
        self.distance = distance
        self.fare = fare
        self.status = status

    def calculate_fare(self):
        if self.fare is None:
            self.fare = self.distance * 2

    def complete_ride(self):
        self.status = 'Completed'


class UberApp:
    def __init__(self):
        # Connect to the database
        self.conn = sqlite3.connect('uber_app.db')  
        self.cursor = self.conn.cursor()
         # Create the necessary tables in the database
        self.create_tables()

    def create_tables(self):
        # Create the drivers table if it doesn't exist
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS drivers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL)")
        # Create the riders table if it doesn't exist
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS riders (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL)")
        # Create the rides table if it doesn't exist
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS rides (id INTEGER PRIMARY KEY AUTOINCREMENT, rider_id INTEGER NOT NULL, driver_id INTEGER NOT NULL, distance REAL NOT NULL, fare REAL, status TEXT NOT NULL)")
        self.conn.commit()

    def register_driver(self, name):
        try:
            # Insert the driver name into the drivers table (case-insensitive)
            self.cursor.execute("INSERT INTO drivers (name) VALUES (?)", (name.lower(),))
            self.conn.commit()
            print(f"Driver '{name}' registered successfully.")
        except sqlite3.Error as e:
            print(f"Error registering driver: {e}")

    def register_rider(self, name):
        try:
            # Insert the rider name into the riders table (case-insensitive)
            self.cursor.execute("INSERT INTO riders (name) VALUES (?)", (name.lower(),))
            self.conn.commit()
            print(f"Rider '{name}' registered successfully.")
        except sqlite3.Error as e:
            print(f"Error registering rider: {e}")

    def request_ride(self, rider_name, distance):
        try:
            # Fetch all available drivers from the drivers table
            self.cursor.execute("SELECT * FROM drivers")
            drivers = self.cursor.fetchall()
            if not drivers:
                print("No drivers available. Please register a driver first.")
                return

            # Randomly select a driver from the available drivers
            driver = Driver(*random.choice(drivers))

            # Check if the rider exists in the riders table (case-insensitive)
            self.cursor.execute("SELECT * FROM riders WHERE lower(name) = ?", (rider_name.lower(),))
            rider = self.cursor.fetchone()
            if not rider:
                print("Invalid rider name.")
                return

            # Insert the ride details into the rides table
            self.cursor.execute(
                "INSERT INTO rides (rider_id, driver_id, distance, status) VALUES (?, ?, ?, ?)",
                (rider[0], driver.id, distance, 'Pending'))
            self.conn.commit()
            ride_id = self.cursor.lastrowid

            # Create a Ride object with the ride details
            ride = Ride(ride_id, Rider(*rider), driver, distance)
            ride.calculate_fare()
            print(f"Ride requested successfully. Driver '{driver.name}' assigned.")
            print(f"Estimated fare: R{ride.fare:.2f}")
        except sqlite3.Error as e:
            print(f"Error requesting ride: {e}")

    def complete_ride(self, rider_name):
        try:
            # Check if the rider exists in the riders table (case-insensitive)
            self.cursor.execute("SELECT * FROM riders WHERE lower(name) = ?", (rider_name.lower(),))
            rider = self.cursor.fetchone()
            if not rider:
                print("Invalid rider name.")
                return

            # Check if there is a pending ride for the given rider name
            self.cursor.execute("SELECT * FROM rides WHERE rider_id = ? AND status = ?", (rider[0], 'Pending'))
            ride = self.cursor.fetchone()
            if not ride:
                print("No pending ride found for the given rider name.")
                return

            # Update the status of the ride to 'Completed' in the rides table
            self.cursor.execute("UPDATE rides SET status = 'Completed' WHERE id = ?", (ride[0],))
            self.conn.commit()

            # Create a Ride object with the ride details
            ride_obj = Ride(*ride[0:6])
            ride_obj.complete_ride()

            if ride_obj.fare is not None:
                print(f"Ride completed. Fare: ${ride_obj.fare:.2f}")
            else:
                print("Ride completed. Fare calculation pending.")
        except sqlite3.Error as e:
            print(f"Error completing ride: {e}")

    def show_ride_status(self, rider_name):
        try:
            # Check if the rider exists in the riders table (case-insensitive)
            self.cursor.execute("SELECT * FROM riders WHERE lower(name) = ?", (rider_name.lower(),))
            rider = self.cursor.fetchone()
            if not rider:
                print("Invalid rider name.")
                return

            # Check if there is a pending ride for the given rider name
            self.cursor.execute("SELECT * FROM rides WHERE rider_id = ? AND status = ?", (rider[0], 'Pending'))
            ride = self.cursor.fetchone()
            if not ride:
                print("No pending ride found for the given rider name.")
                return

            # Fetch the driver details for the ride from the drivers table
            self.cursor.execute("SELECT * FROM drivers WHERE id = ?", (ride[2],))
            driver = self.cursor.fetchone()

            # Create a Ride object with the ride details
            ride_obj = Ride(*ride)
            print(f"Ride Status: {ride_obj.status}")
            print(f"Driver: {driver[1]}")
            print(f"Distance: {ride_obj.distance} km")
            if ride_obj.fare is not None:
                print(f"Estimated Fare: ${ride_obj.fare:.2f}")
            else:
                print("Fare calculation pending.")
        except sqlite3.Error as e:
            print(f"Error showing ride status: {e}")

    def __del__(self):
        self.conn.close()


# Example usage with user input
app = UberApp()

while True:
    print("\n--- Uber App ---")
    print("1. Register Driver")
    print("2. Register Rider")
    print("3. Request Ride")
    print("4. Complete Ride")
    print("5. Show Ride Status")
    print("6. Quit")
    choice = input("Enter your choice: ")

    if choice == '1':
        name = input("Enter driver name: ")
        app.register_driver(name)
    elif choice == '2':
        name = input("Enter rider name: ")
        app.register_rider(name)
    elif choice == '3':
        name = input("Enter rider name: ")
        distance = float(input("Enter distance (in km): "))
        app.request_ride(name, distance)
    elif choice == '4':
        name = input("Enter rider name: ")
        app.complete_ride(name)
    elif choice == '5':
        name = input("Enter rider name: ")
        app.show_ride_status(name)
    elif choice == '6':
        print("Goodbye,thank you for using our services")
        break
    else:
        print("Invalid choice. Please try again.")
