import re
from src.database import DatabaseConnection


class ActiveRecord:
    def save(self):
        raise NotImplementedError("Subclasses must implement save method")


class Category(ActiveRecord):
    def __init__(self, name):
        self.name = name
        self.category_id = None

    def save(self):
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


class Order(ActiveRecord):
    def __init__(self, customer_id, items):
        self.customer_id = int(customer_id)
        self.items = items

    def save_transaction(self):
        if not self.items:
            raise ValueError("Cannot create empty order")

        connection = DatabaseConnection.get_connection()
        try:
            connection.rollback()
        except:
            pass

        connection.start_transaction()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT customer_id FROM customers WHERE customer_id = %s", (self.customer_id,))
            if not cursor.fetchone():
                raise ValueError(f"Customer ID {self.customer_id} does not exist")

            cursor.execute("INSERT INTO orders (customer_id, status) VALUES (%s, 'PENDING')", (self.customer_id,))
            order_id = cursor.lastrowid

            for item in self.items:
                product_id = item.get('product_id')
                quantity = item.get('quantity')

                if not product_id or not quantity or int(quantity) <= 0:
                    raise ValueError("Invalid product ID or quantity")

                cursor.execute("SELECT price, stock_quantity FROM products WHERE product_id=%s", (product_id,))
                result = cursor.fetchone()
                if not result:
                    raise ValueError(f"Product {product_id} not found")

                price, stock = result
                if stock < int(quantity):
                    raise ValueError(f"Insufficient stock for product {product_id}. Available: {stock}")

                cursor.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (%s, %s, %s, %s)",
                    (order_id, product_id, quantity, float(price)))

                cursor.execute("UPDATE products SET stock_quantity=%s WHERE product_id=%s",
                               (stock - int(quantity), product_id))

            connection.commit()
            return True
        except Exception as error:
            connection.rollback()
            raise error
        finally:
            cursor.close()

    @staticmethod
    def update_status(order_id, new_status):
        valid_statuses = ['PENDING', 'PAID', 'SHIPPED', 'CANCELLED']
        if new_status not in valid_statuses:
            raise ValueError("Invalid status")

        connection = DatabaseConnection.get_connection()
        try:
            connection.rollback()
        except:
            pass

        connection.start_transaction()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT status FROM orders WHERE order_id = %s", (order_id,))
            result = cursor.fetchone()
            if not result:
                raise ValueError("Order not found")
            old_status = result[0]

            if old_status == 'CANCELLED' and new_status != 'CANCELLED':
                raise ValueError("Cannot reactivate a cancelled order. Please create a new one.")

            cursor.execute("UPDATE orders SET status = %s WHERE order_id = %s", (new_status, order_id))

            if new_status == 'CANCELLED' and old_status != 'CANCELLED':
                cursor.execute("SELECT product_id, quantity FROM order_items WHERE order_id = %s", (order_id,))
                items = cursor.fetchall()
                for pid, qty in items:
                    cursor.execute("UPDATE products SET stock_quantity = stock_quantity + %s WHERE product_id = %s",
                                   (qty, pid))

            connection.commit()
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            cursor.close()

    @staticmethod
    def delete_transaction(order_id):
        connection = DatabaseConnection.get_connection()
        try:
            connection.rollback()
        except:
            pass

        connection.start_transaction()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT status FROM orders WHERE order_id = %s", (order_id,))
            status_res = cursor.fetchone()
            if status_res and status_res[0] != 'CANCELLED':
                cursor.execute("SELECT product_id, quantity FROM order_items WHERE order_id = %s", (order_id,))
                items = cursor.fetchall()
                for product_id, quantity in items:
                    cursor.execute("UPDATE products SET stock_quantity = stock_quantity + %s WHERE product_id = %s",
                                   (quantity, product_id))

            cursor.execute("DELETE FROM order_items WHERE order_id = %s", (order_id,))
            cursor.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))

            connection.commit()
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            cursor.close()