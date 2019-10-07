#!/usr/bin/env python3

import sqlite3 

class DataBase:

    def __init__(self, name):
        self.connection = None
        self.db_file = name
        self.jobs_queue = []

    def work_on_db(func):
        """ Decorating functions to open and close connection DB automatically """
        def wrapper(self):
            self.create_connection()
            func(self)
            self.close_connection()
        return wrapper
    
    @work_on_db
    def create_table(self, name="hello"):
        print("Not implemented")
    
    def create_connection(self):
        if TEST:
            print("Connecting")
        try:
            conn = sqlite3.connect(self.db_file)
        except Error as e:
            print(e)
        finally:
            if conn:
                self.connection = conn 

    def close_connection(self):
        if TEST : 
            print("Closing")
        if self.connection:
            self.connection.close()
            self.connection = None


if __name__=="__main__":
    import os 
    TEST = True

    name = "test.db"
    print("Creating a test database file.")
    db = DataBase(name)
    db.create_table()
    if os.path.exists(name):
        print("Test success, Databse created")
        try:
            os.remove(name)
            print("Database removed")
        except Error as e:
            print("Error : Database not removed.", e)
    else:
        print("Test unsuccessful.")

