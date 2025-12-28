from src.database import DatabaseConnection


class Product:
    def __init__(self, name, price, stock_quantity, category_id, product_id=None):
        self.product_id = product_id
        self.name = name
        self.price = float(price)
        self.stock_quantity = int(stock_quantity)
        self.category_id = int(category_id)

    def save(self):
        connection = DatabaseConnection.get_connection()
        cursor = connection.cursor()

        if self.product_id:
            query = f"UPDATE products SET name='{self.name}', price={self.price}, stock_quantity={self.stock_quantity} WHERE product_id={self.product_id}"
            cursor.execute(query)
        else:
            query = f"INSERT INTO products (name, price, stock_quantity, category_id) VALUES ('{self.name}', {self.price}, {self.stock_quantity}, {self.category_id})"
            cursor.execute(query)
            self.product_id = cursor.lastrowid

        connection.commit()


class Order:
    def __init__(self, customer_id, items):
        self.customer_id = int(customer_id)
        self.items = items

    def save_transaction(self):
        connection = DatabaseConnection.get_connection()
        cursor = connection.cursor()

        cursor.execute(f"SELECT customer_id FROM customers WHERE customer_id = {self.customer_id}")
        if not cursor.fetchone():
            return False

        cursor.execute(f"INSERT INTO orders (customer_id, status) VALUES ({self.customer_id}, 'PENDING')")
        order_id = cursor.lastrowid

        for item in self.items:
            product_id = item['product_id']
            quantity = int(item['quantity'])

            cursor.execute(f"SELECT price, stock_quantity FROM products WHERE product_id={product_id}")
            result = cursor.fetchone()

            if not result:
                return False

            price, stock = result

            if stock < quantity:
                return False

            cursor.execute(
                f"INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES ({order_id}, {product_id}, {quantity}, {price})")

            new_stock = stock - quantity
            cursor.execute(f"UPDATE products SET stock_quantity={new_stock} WHERE product_id={product_id}")

        connection.commit()
        return True