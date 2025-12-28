import sys
import os

sys.path.append(os.getcwd())

from src.database import DatabaseConnection
from src.models import Product, Order


def run_test():
    print("--- TEST 1: Database Initialization ---")
    try:
        DatabaseConnection.initialize_database()
        print("SUCCESS: Database connected and initialized.")
    except Exception as error:
        print(f"FAILED: {error}")
        return

    print("\n--- TEST 2: Create and Save Product ---")
    try:
        new_product = Product(
            name="Test Python Book",
            price=500.00,
            stock_quantity=10,
            category_id=1
        )
        new_product.save()

        if new_product.product_id:
            print(f"SUCCESS: Product saved. New ID is: {new_product.product_id}")
        else:
            print("FAILED: Product ID is missing.")
            return
    except Exception as error:
        print(f"FAILED: {error}")
        return

    print("\n--- TEST 3: Create Order (Transaction) ---")
    try:
        customer_id = 1

        items_to_order = [
            {
                'product_id': new_product.product_id,
                'quantity': 2
            }
        ]

        new_order = Order(customer_id, items_to_order)
        result = new_order.save_transaction()

        if result:
            print("SUCCESS: Transaction completed. Order saved, stock reduced.")
        else:
            print("FAILED: Transaction returned False.")

    except Exception as error:
        print(f"FAILED: {error}")


if __name__ == "__main__":
    run_test()