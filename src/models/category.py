from src.models.base import ActiveRecord
from src.database.connection import DatabaseConnection


class Category(ActiveRecord):
    """
    represents product category
    """
    def __init__(self, name):
        self.name = name
        self.category_id = None

    def save(self):
        """
        Checks if a category with the same name exists.
        If yes, retrieves its ID. If no, creates a new record
        :return:
        """
        if not self.name:
            raise ValueError("Category name cannot be empty")

        connection = DatabaseConnection.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT category_id FROM categories WHERE name = %s", (self.name,))
            result = cursor.fetchone()
            if result:
                self.category_id = result[0]
            else:
                cursor.execute("INSERT INTO categories (name) VALUES (%s)", (self.name,))
                self.category_id = cursor.lastrowid
            connection.commit()
        except Exception as e:
            raise e
        finally:
            cursor.close()