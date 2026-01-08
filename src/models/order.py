from src.models.base import ActiveRecord
from src.database.connection import DatabaseConnection


class Order(ActiveRecord):
    """
    Represents an order
    """
    def __init__(self, customer_id, items):
        """

        :param customer_id:
        :param items: List of dictionaries [{'product_id': x, 'quantity': y}]
        """
        self.customer_id = int(customer_id)
        self.items = items

    def save_transaction(self):
        """
        Executes a complex transaction:
        1. Checks if customer exists
        2. Creates order record
        3. Iterates through items, checks stock availability
        4. Creates order_items records
        5. Updates (decreases) product stock
        """
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
        """
        Updates status of an order
        """
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
        """
        1. Returns items to stock (if order wasn't cancelled already)
        2. Deletes records from order_items
        3. Deletes record from orders
        """
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