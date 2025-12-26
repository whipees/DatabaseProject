import mysql.connector
from mysql.connector import Error


def test_sql_connection():
    """
    A simple script to test MySQL connectivity without config files or classes.
    """
    connection = None
    try:
        db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'port': 3306,
            'database': 'test_db'
        }


        connection = mysql.connector.connect(**db_config)

        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"2. SUCCESS! Connected to MySQL Server version {db_info}")

            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            record = cursor.fetchone()
            print(f"3. Current Database context: {record[0]}")

    except Error as e:
        print(f"Message: {e.msg}")


    finally:
        if connection is not None and connection.is_connected():
            connection.close()
            print("\n4. Connection closed.")


if __name__ == '__main__':
    test_sql_connection()