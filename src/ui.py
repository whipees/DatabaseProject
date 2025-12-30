import tkinter
from tkinter import ttk, messagebox, filedialog
import json
import os
from src.database import DatabaseConnection
from src.models import Order, Product

class ApplicationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Store Manager System (D2)")
        self.root.geometry("900x600")

        DatabaseConnection.initialize_database()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both')

        self.setup_order_tab()
        self.setup_products_tab()
        self.setup_report_tab()
        self.setup_import_tab()

    def setup_order_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="New Order")

        ttk.Label(frame, text="Customer ID (Default: 1):").pack(pady=5)
        self.customer_entry = ttk.Entry(frame)
        self.customer_entry.pack()

        ttk.Label(frame, text="Product ID:").pack(pady=5)
        self.product_entry = ttk.Entry(frame)
        self.product_entry.pack()

        ttk.Label(frame, text="Quantity:").pack(pady=5)
        self.quantity_entry = ttk.Entry(frame)
        self.quantity_entry.pack()

        ttk.Button(frame, text="Create Order (Transaction)", command=self.create_order).pack(pady=20)

    def setup_products_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Products Inventory")

        ttk.Button(frame, text="Refresh Stock", command=lambda: self.load_products(frame)).pack(pady=10)

        columns = ('ID', 'Name', 'Price', 'Stock', 'Category')
        self.products_tree = ttk.Treeview(frame, columns=columns, show='headings')

        self.products_tree.heading('ID', text='ID')
        self.products_tree.column('ID', width=50)

        self.products_tree.heading('Name', text='Product Name')
        self.products_tree.column('Name', width=200)

        self.products_tree.heading('Price', text='Price')
        self.products_tree.column('Price', width=100)

        self.products_tree.heading('Stock', text='Stock Qty')
        self.products_tree.column('Stock', width=100)

        self.products_tree.heading('Category', text='Category ID')
        self.products_tree.column('Category', width=100)

        self.products_tree.pack(expand=True, fill='both')

        self.load_products(frame)

    def setup_report_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Sales Report")

        ttk.Button(frame, text="Refresh Report", command=lambda: self.load_report(frame)).pack(pady=10)

        columns = ('ID', 'Customer', 'Date', 'Status', 'Total')
        self.tree = ttk.Treeview(frame, columns=columns, show='headings')

        self.tree.heading('ID', text='Order ID')
        self.tree.column('ID', width=50)

        self.tree.heading('Customer', text='Customer Name')
        self.tree.column('Customer', width=200)

        self.tree.heading('Date', text='Date')
        self.tree.column('Date', width=150)

        self.tree.heading('Status', text='Status')
        self.tree.column('Status', width=100)

        self.tree.heading('Total', text='Total Amount')
        self.tree.column('Total', width=100)

        self.tree.pack(expand=True, fill='both')

    def setup_import_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Import")
        ttk.Button(frame, text="Import JSON Data", command=self.import_json).pack(pady=50)

    def create_order(self):
        customer_input = self.customer_entry.get()
        product_input = self.product_entry.get()
        quantity_input = self.quantity_entry.get()

        if customer_input and product_input and quantity_input:
            customer_id = int(customer_input)
            product_id = int(product_input)
            quantity = int(quantity_input)

            if quantity > 0:
                order = Order(customer_id, [{'product_id': product_id, 'quantity': quantity}])
                order.save_transaction()
                messagebox.showinfo("Success", "Order successfully created!")

                self.customer_entry.delete(0, tkinter.END)
                self.product_entry.delete(0, tkinter.END)
                self.quantity_entry.delete(0, tkinter.END)

                self.load_products(None)
            else:
                messagebox.showwarning("Validation Error", "Quantity must be greater than 0.")
        else:
            messagebox.showwarning("Validation Error", "All fields must be filled.")

    def load_products(self, frame):
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)

        connection = DatabaseConnection.get_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT product_id, name, price, stock_quantity, category_id FROM products")
            rows = cursor.fetchall()
            for row in rows:
                self.products_tree.insert('', 'end', values=row)
            cursor.close()

    def load_report(self, frame):
        for item in self.tree.get_children():
            self.tree.delete(item)

        connection = DatabaseConnection.get_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM view_order_summary")
            rows = cursor.fetchall()
            for row in rows:
                self.tree.insert('', 'end', values=row)
            cursor.close()

    def import_json(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if filepath:
            with open(filepath, 'r') as file:
                data = json.load(file)

            if isinstance(data, list):
                success_count = 0
                for item in data:
                    if 'name' in item and 'price' in item and 'stock' in item and 'category_id' in item:
                        product = Product(item['name'], item['price'], item['stock'], item['category_id'])
                        product.save()
                        success_count += 1

                messagebox.showinfo("Import Result", f"Successfully imported {success_count} products.")
                self.load_products(None)