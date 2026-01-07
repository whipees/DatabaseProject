import tkinter
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import os
from src.database import DatabaseConnection
from src.models import Order, Product, Category, Customer

class ApplicationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Store Manager System (D2)")
        self.root.geometry("1000x700")

        DatabaseConnection.initialize_database()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both')

        self.setup_order_tab()
        self.setup_products_tab()
        self.setup_customers_tab()
        self.setup_report_tab()
        self.setup_import_tab()

    def setup_order_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="New Order")

        ttk.Label(frame, text="Customer ID:").pack(pady=5)
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
        self.notebook.add(frame, text="Products")

        form_frame = ttk.LabelFrame(frame, text="Add New Product")
        form_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        self.prod_name_entry = ttk.Entry(form_frame)
        self.prod_name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Price:").grid(row=0, column=2, padx=5, pady=5)
        self.prod_price_entry = ttk.Entry(form_frame)
        self.prod_price_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form_frame, text="Stock:").grid(row=0, column=4, padx=5, pady=5)
        self.prod_stock_entry = ttk.Entry(form_frame)
        self.prod_stock_entry.grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(form_frame, text="Category ID:").grid(row=0, column=6, padx=5, pady=5)
        self.prod_cat_entry = ttk.Entry(form_frame, width=5)
        self.prod_cat_entry.grid(row=0, column=7, padx=5, pady=5)

        ttk.Button(form_frame, text="Add Product", command=self.create_product).grid(row=0, column=8, padx=10, pady=5)

        controls = ttk.Frame(frame)
        controls.pack(pady=10)

        ttk.Button(controls, text="Refresh Stock", command=lambda: self.load_products(frame)).pack(side='left', padx=10)
        ttk.Button(controls, text="Add Stock (Restock)", command=self.add_product_stock).pack(side='left', padx=10)

        columns = ('ID', 'Name', 'Price', 'Stock', 'Category')
        self.products_tree = ttk.Treeview(frame, columns=columns, show='headings')
        self.products_tree.heading('ID', text='ID')
        self.products_tree.heading('Name', text='Name')
        self.products_tree.heading('Price', text='Price')
        self.products_tree.heading('Stock', text='Stock')
        self.products_tree.heading('Category', text='Category ID')
        self.products_tree.pack(expand=True, fill='both')
        self.load_products(frame)

    def setup_customers_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Customers")

        form_frame = ttk.LabelFrame(frame, text="Add New Customer")
        form_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(form_frame, text="First Name:").grid(row=0, column=0, padx=5, pady=5)
        self.cust_first_entry = ttk.Entry(form_frame)
        self.cust_first_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Last Name:").grid(row=0, column=2, padx=5, pady=5)
        self.cust_last_entry = ttk.Entry(form_frame)
        self.cust_last_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form_frame, text="Email:").grid(row=0, column=4, padx=5, pady=5)
        self.cust_email_entry = ttk.Entry(form_frame)
        self.cust_email_entry.grid(row=0, column=5, padx=5, pady=5)

        ttk.Button(form_frame, text="Add Customer", command=self.create_customer).grid(row=0, column=6, padx=10, pady=5)

        ttk.Button(frame, text="Refresh Customers", command=lambda: self.load_customers(frame)).pack(pady=5)

        columns = ('ID', 'First', 'Last', 'Email')
        self.customers_tree = ttk.Treeview(frame, columns=columns, show='headings')
        self.customers_tree.heading('ID', text='ID')
        self.customers_tree.heading('First', text='First')
        self.customers_tree.heading('Last', text='Last')
        self.customers_tree.heading('Email', text='Email')
        self.customers_tree.pack(expand=True, fill='both')
        self.load_customers(frame)

    def setup_report_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Orders Management")

        controls_frame = ttk.Frame(frame)
        controls_frame.pack(pady=10, fill='x')

        ttk.Button(controls_frame, text="Refresh", command=lambda: self.load_report(frame)).pack(side='left', padx=10)

        ttk.Label(controls_frame, text="New Status:").pack(side='left')
        self.status_var = tkinter.StringVar()
        self.status_combo = ttk.Combobox(controls_frame, textvariable=self.status_var, state="readonly", width=10)
        self.status_combo['values'] = ('PENDING', 'PAID', 'SHIPPED', 'CANCELLED')
        self.status_combo.current(0)
        self.status_combo.pack(side='left', padx=5)
        ttk.Button(controls_frame, text="Update Status", command=self.update_order_status).pack(side='left', padx=5)

        ttk.Button(controls_frame, text="DELETE ORDER (Transaction)", command=self.delete_order).pack(side='right', padx=20)

        columns = ('ID', 'Customer', 'Date', 'Status', 'Total')
        self.report_tree = ttk.Treeview(frame, columns=columns, show='headings')
        self.report_tree.heading('ID', text='ID')
        self.report_tree.heading('Customer', text='Customer')
        self.report_tree.heading('Date', text='Date')
        self.report_tree.heading('Status', text='Status')
        self.report_tree.heading('Total', text='Total')
        self.report_tree.pack(expand=True, fill='both')
        self.load_report(frame)

    def setup_import_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Import")
        ttk.Label(frame, text="Expected JSON: [{'category': 'Name', 'name': 'Prod', 'price': 10, 'stock': 5}]").pack(pady=10)
        ttk.Button(frame, text="Import JSON Data", command=self.import_json).pack(pady=20)

    def create_order(self):
        c_val = self.customer_entry.get()
        p_val = self.product_entry.get()
        q_val = self.quantity_entry.get()

        if c_val and p_val and q_val:
            c_id = int(c_val)
            p_id = int(p_val)
            qty = int(q_val)

            if qty > 0:
                order = Order(c_id, [{'product_id': p_id, 'quantity': qty}])
                order.save_transaction()
                messagebox.showinfo("Success", "Order Created!")

                self.customer_entry.delete(0, tkinter.END)
                self.product_entry.delete(0, tkinter.END)
                self.quantity_entry.delete(0, tkinter.END)
                self.load_products(None)
            else:
                messagebox.showwarning("Validation Error", "Quantity must be greater than 0.")
        else:
            messagebox.showwarning("Validation Error", "All fields must be filled.")

    def create_product(self):
        name = self.prod_name_entry.get()
        price_val = self.prod_price_entry.get()
        stock_val = self.prod_stock_entry.get()
        cat_val = self.prod_cat_entry.get()

        if name and price_val and stock_val and cat_val:
            try:
                price = float(price_val)
                stock = int(stock_val)
                cat_id = int(cat_val)

                product = Product(name, price, stock, cat_id)
                product.save()
                messagebox.showinfo("Success", "Product Added!")

                self.prod_name_entry.delete(0, tkinter.END)
                self.prod_price_entry.delete(0, tkinter.END)
                self.prod_stock_entry.delete(0, tkinter.END)
                self.prod_cat_entry.delete(0, tkinter.END)
                self.load_products(None)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            messagebox.showwarning("Validation Error", "All fields must be filled.")

    def create_customer(self):
        first = self.cust_first_entry.get()
        last = self.cust_last_entry.get()
        email = self.cust_email_entry.get()

        if first and last and email:
            customer = Customer(first, last, email)
            customer.save()
            messagebox.showinfo("Success", "Customer Added!")

            self.cust_first_entry.delete(0, tkinter.END)
            self.cust_last_entry.delete(0, tkinter.END)
            self.cust_email_entry.delete(0, tkinter.END)
            self.load_customers(None)
        else:
            messagebox.showwarning("Validation Error", "All fields must be filled.")

    def add_product_stock(self):
        selected = self.products_tree.selection()
        if selected:
            product_id = self.products_tree.item(selected)['values'][0]
            quantity = simpledialog.askinteger("Restock", "Enter quantity to add:", parent=self.root, minvalue=1)

            if quantity:
                Product.add_stock(product_id, quantity)
                messagebox.showinfo("Success", "Stock updated.")
                self.load_products(None)
        else:
            messagebox.showwarning("Warning", "Select a product first.")

    def update_order_status(self):
        selected_item = self.report_tree.selection()
        if selected_item:
            order_id = self.report_tree.item(selected_item)['values'][0]
            Order.update_status(order_id, self.status_var.get())
            self.load_report(None)
        else:
            messagebox.showwarning("Selection Error", "Please select an order.")

    def delete_order(self):
        selected_item = self.report_tree.selection()
        if selected_item:
            order_id = self.report_tree.item(selected_item)['values'][0]
            if messagebox.askyesno("Confirm", f"Delete Order {order_id}? Items will return to stock."):
                Order.delete_transaction(order_id)
                messagebox.showinfo("Success", "Order Deleted & Stock Returned.")
                self.load_report(None)
                self.load_products(None)
        else:
            messagebox.showwarning("Warning", "Select an order to delete.")

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

    def load_customers(self, frame):
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)

        connection = DatabaseConnection.get_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT customer_id, first_name, last_name, email FROM customers")
            rows = cursor.fetchall()
            for row in rows:
                self.customers_tree.insert('', 'end', values=row)
            cursor.close()

    def load_report(self, frame):
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)

        connection = DatabaseConnection.get_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM view_order_summary ORDER BY order_id DESC")
            rows = cursor.fetchall()
            for row in rows:
                self.report_tree.insert('', 'end', values=row)
            cursor.close()

    def import_json(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if filepath:
            with open(filepath, 'r') as file:
                data = json.load(file)

            if isinstance(data, list):
                count = 0
                for item in data:
                    if 'category' in item and 'name' in item and 'price' in item and 'stock' in item:
                        category = Category(item['category'])
                        category.save()

                        product = Product(item['name'], item['price'], item['stock'], category.category_id)
                        product.save()
                        count += 1

                messagebox.showinfo("Success", f"Imported {count} items.")
                self.load_products(None)