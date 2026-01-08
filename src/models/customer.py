import re
from src.models.base import ActiveRecord
from src.database.connection import DatabaseConnection


class Customer(ActiveRecord):
    def __init__(self, first_name, last_name, email, customer_id=None):
        self.customer_id = customer_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

    def validate(self):
        if not self.first_name or not self.last_name:
            raise ValueError("Name cannot be empty")

        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, self.email):
            raise ValueError("Invalid email format")

    def save(self):
        self.validate()
        connection = DatabaseConnection.get_connection()
        cursor = connection.cursor()
        try:
            if self.customer_id:
                query = "UPDATE customers SET first_name=%s, last_name=%s, email=%s WHERE customer_id=%s"
                cursor.execute(query, (self.first_name, self.last_name, self.email, self.customer_id))
            else:
                query = "INSERT INTO customers (first_name, last_name, email) VALUES (%s, %s, %s)"
                cursor.execute(query, (self.first_name, self.last_name, self.email))
                self.customer_id = cursor.lastrowid
            connection.commit()
        finally:
            cursor.close()