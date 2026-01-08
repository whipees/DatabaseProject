from src.models.base import ActiveRecord
from src.database.connection import DatabaseConnection


class Product(ActiveRecord):
    def __init__(self, name, price, stock_quantity, category_id, product_id=None):
        self.product_id = product_id
        self.name = name
        self.price = float(price)
        self.stock_quantity = int(stock_quantity)
        self.category_id = int(category_id)

    def validate(self):
        if not self.name:
            raise ValueError("Product name cannot be empty")
        if self.price < 0:
            raise ValueError("Price cannot be negative")
        if self.stock_quantity < 0:
            raise ValueError("Stock cannot be negative")

    def save(self):
        self.validate()
        connection = DatabaseConnection.get_connection()
        try:
            connection.rollback()
        except:
            pass

        cursor = connection.cursor()
        try:
            if self.product_id:
                query = "UPDATE products SET name=%s, price=%s, stock_quantity=%s WHERE product_id=%s"
                cursor.execute(query, (self.name, self.price, self.stock_quantity, self.product_id))
            else:
                query = "INSERT INTO products (name, price, stock_quantity, category_id) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (self.name, self.price, self.stock_quantity, self.category_id))
                self.product_id = cursor.lastrowid
            connection.commit()
        finally:
            cursor.close()

    @staticmethod
    def add_stock(product_id, quantity):
        if quantity <= 0:
            raise ValueError("Quantity to add must be positive")

        connection = DatabaseConnection.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("UPDATE products SET stock_quantity = stock_quantity + %s WHERE product_id = %s",
                           (quantity, product_id))
            connection.commit()
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            cursor.close()

    @staticmethod
    def delete_product(product_id):
        connection = DatabaseConnection.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
            if cursor.rowcount == 0:
                raise ValueError("Product not found.")
            connection.commit()
        except Exception as e:
            connection.rollback()
            if "foreign key constraint fails" in str(e).lower():
                raise ValueError("Cannot delete product: It is part of existing orders. Delete the orders first.")
            raise e
        finally:
            cursor.close()