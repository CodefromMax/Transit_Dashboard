from sqlalchemy import create_engine, text
import configparser
from helper.find_project_root import find_project_root
import pandas as pd
import os
from urllib.parse import quote_plus

class DatabaseEngine:
    """
    This class should be for any SQL operations that require dataframe integration.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseEngine, cls).__new__(cls)
            cls._instance._initialize_engine()
        return cls._instance

    def _initialize_engine(self):
        config = configparser.ConfigParser()

        project_root = find_project_root("Transit_Dashboard")
        config_path = os.path.join(project_root, "src/helper/config.cfg")
        config.read(config_path)

        if 'mysql' not in config:
            raise KeyError("Section 'mysql' not found in config file.")

        try:
            user = config['mysql']['user']
            password = quote_plus(config['mysql']['password'])  # URL encode the password
            host = config['mysql']['host']
            port = config['mysql']['port']
            database = config['mysql']['database']
        
            url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
            
            self.engine = create_engine(url)
            print("Successfully created database engine")
        except Exception as e:
            print(f"Error creating database engine: {e}")
            raise

    def get_engine(self):
        return self.engine

    def dispose_engine(self):
        if self.engine:
            self.engine.dispose()
            print("Engine disposed")

    def select_query(self, query, params=None):
        """
        Execute a SELECT query and return results as a DataFrame
        
        Example:
        result = engine.select_query(
            "SELECT * FROM users WHERE age > :age AND city = :city",
            params={"age": 25, "city": "New York"}
        )
        """
        try:
            with self.engine.connect() as connection:
                if params:
                    result = pd.read_sql(text(query), connection, params=params)
                else:
                    result = pd.read_sql(text(query), connection)
                return result
        except Exception as e:
            print(f"Error executing SELECT query: {e}")
            raise

    def write_query(self, query, params=None):
        """
        Execute an INSERT query
        
        Example:
        engine.write_query(
            "INSERT INTO users (name, age) VALUES (:name, :age)",
            params={"name": "John", "age": 30}
        )
        """
        try:
            with self.engine.connect() as connection:
                with connection.begin():
                    if params:
                        connection.execute(text(query), parameters=params)
                    else:
                        connection.execute(text(query))
            print("Write query executed successfully")
        except Exception as e:
            print(f"Error executing INSERT query: {e}")
            raise

    def update_query(self, query, params=None):
        """
        Execute an UPDATE query
        
        Example:
        engine.update_query(
            "UPDATE users SET age = :new_age WHERE name = :name",
            params={"new_age": 31, "name": "John"}
        )
        """
        try:
            with self.engine.connect() as connection:
                with connection.begin():
                    if params:
                        result = connection.execute(text(query), parameters=params)
                    else:
                        result = connection.execute(text(query))
                print(f"Updated {result.rowcount} rows")
            return result.rowcount
        except Exception as e:
            print(f"Error executing UPDATE query: {e}")
            raise

    def delete_query(self, query, params=None):
        """
        Execute a DELETE query
        
        Example:
        engine.delete_query(
            "DELETE FROM users WHERE age < :age",
            params={"age": 25}
        )
        """
        try:
            with self.engine.connect() as connection:
                with connection.begin():
                    if params:
                        result = connection.execute(text(query), parameters=params)
                    else:
                        result = connection.execute(text(query))
                print(f"Deleted {result.rowcount} rows")
            return result.rowcount
        except Exception as e:
            print(f"Error executing DELETE query: {e}")
            raise
    
    def delete_table(self, table_name):
        """
        Delete a table from the database
        
        Args:
            table_name (str): Name of the table to delete
        
        Example:
            engine.delete_table("users")
        """
        try:
            with self.engine.connect() as connection:
                with connection.begin():
                    connection.execute(text(f"DROP TABLE {table_name}"))
                    print(f"Table {table_name} successfully deleted")
        except Exception as e:
            print(f"Error deleting table: {e}")
            raise
    
    def write_dataframe(self, df, table_name, if_exists='append'):
        """Write a pandas DataFrame to a SQL table"""
        try:
            df.to_sql(
                name=table_name,
                con=self.engine,
                if_exists=if_exists,
                index=False
            )
            print(f"Successfully wrote DataFrame to {table_name}")
        except Exception as e:
            print(f"Error writing DataFrame to database: {e}")
            raise