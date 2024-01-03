# db_connector.py
import mysql.connector

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='',
            database='22mmcb02'
        )
        print("Connected to MySQL Database")
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

def execute_query(connection, query, data=None):
    try:
        cursor = connection.cursor()
        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)
        result = cursor.fetchall()  # Fetch the result of the query
        return result
    except Exception as e:
        print(f"Error executing query: {e}")
    finally:
        cursor.close()

def close_connection(connection):
    try:
        connection.close()
    except Exception as e:
        print(f"Error closing connection: {e}")