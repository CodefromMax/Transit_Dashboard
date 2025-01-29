import pymysql
from pymysql import Error
import configparser
import os
from helper.find_project_root import find_project_root

class DatabaseConnector:
    """
    This class should be used direct SQL queries and operations, without dataframe integration.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnector, cls).__new__(cls)
            cls._instance._initialize_connection()
        return cls._instance

    def _initialize_connection(self):
        config = configparser.ConfigParser()

        project_root = find_project_root("Transit_Dashboard")
        config_path = os.path.join(project_root, "src/helper/config.cfg")
        config.read(config_path)

        if 'mysql' not in config:
            raise KeyError("Section 'mysql' not found in config file.")

        self.connection = None
        try:
            self.connection = pymysql.connect(
                host=config['mysql']['host'],
                user=config['mysql']['user'],
                password=config['mysql']['password'],
                database=config['mysql']['database'],
                port=int(config['mysql']['port']),
                cursorclass=pymysql.cursors.DictCursor  # Optional: Use DictCursor for results as dictionaries
            )
            print("Successfully connected to the database")
        except Error as e:
            print(f"Error connecting to the database: {e}")
            raise  # Re-raise the exception to stop execution

    def get_connection(self):
        return self.connection

    def close_connection(self):
        if self.connection:
            self.connection.close()
            print("Connection closed")

    def execute_query(self, query, params=None):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                self.connection.commit()
                return cursor.fetchall()
        except Error as e:
            print(f"Error executing query: {e}")
            raise