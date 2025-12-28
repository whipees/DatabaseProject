import mysql.connector
import configparser
import os


class DatabaseConnection:
    _instance = None

    @staticmethod
    def _load_config():
        config = configparser.ConfigParser()
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_path, 'config', 'settings.ini')

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file missing at: {config_path}")

        try:
            config.read(config_path)
            if 'mysql' not in config:
                raise KeyError("Section [mysql] is missing in settings.ini")

            required_keys = ['host', 'user', 'password', 'database']
            for key in required_keys:
                if key not in config['mysql']:
                    raise KeyError(f"Missing key '{key}' in configuration")

            return config['mysql']
        except Exception as error:
            raise Exception(f"Configuration Error: {str(error)}")

    @staticmethod
    def get_connection(db_check=True):
        if DatabaseConnection._instance is None or not DatabaseConnection._instance.is_connected():
            try:
                db_config = DatabaseConnection._load_config()
                DatabaseConnection._instance = mysql.connector.connect(
                    host=db_config['host'],
                    user=db_config['user'],
                    password=db_config['password'],
                    database=db_config['database'] if db_check else None,
                    port=int(db_config.get('port', 3306)),
                    connection_timeout=5
                )
            except mysql.connector.Error as err:
                if err.errno == 1049:
                    return None
                raise Exception(f"Database Connection Failed: {err}")
            except Exception as e:
                raise e

        return DatabaseConnection._instance