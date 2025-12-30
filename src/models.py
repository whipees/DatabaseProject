from src.database import DatabaseConnection


class ActiveRecord:
    def save(self):
        raise NotImplementedError("Subclasses must implement save method")


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