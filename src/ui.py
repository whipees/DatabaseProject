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

        try:
            DatabaseConnection.initialize_database()
        except Exception as error:
            messagebox.showerror("Critical Error", f"Database Init Failed:\n{error}\nApplication will close.")
            self.root.destroy()
            return

        self.customer_map = {}
        self.product_map = {}

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

        ttk.Label(frame, text="Select Customer:").pack(pady=5)
        self.customer_combo = ttk.Combobox(frame, state="readonly", width=40)
        self.customer_combo.pack()

        ttk.Label(frame, text="Select Product:").pack(pady=5)
        self.product_combo = ttk.Combobox(frame, state="readonly", width=40)
        self.product_combo.pack()

        ttk.Label(frame, text="Quantity:").pack(pady=5)
        self.quantity_entry = ttk.Entry(frame)
        self.quantity_entry.pack()

        ttk.Button(frame, text="Refresh Data", command=self.refresh_dropdowns).pack(pady=5)
        ttk.Button(frame, text="Create Order (Transaction)", command=self.create_order).pack(pady=20)

        self.refresh_dropdowns()

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

        ttk.Label(form_frame, text="Category Name:").grid(row=0, column=6, padx=5, pady=5)
        self.prod_cat_entry = ttk.Entry(form_frame, width=15)
        self.prod_cat_entry.grid(row=0, column=7, padx=5, pady=5)

        ttk.Button(form_frame, text="Add Product", command=self.create_product).grid(row=0, column=8, padx=10, pady=5)

        controls = ttk.Frame(frame)
        controls.pack(pady=10)
        ttk.Button(controls, text="Refresh Stock", command=lambda: self.load_products(frame)).pack(side='left', padx=10)
        ttk.Button(controls, text="Add Stock (Restock)", command=self.add_product_stock).pack(side='left', padx=10)

        columns = ('ID', 'Name', 'Price', 'Stock', 'Category Name')
        self.products_tree = ttk.Treeview(frame, columns=columns, show='headings')
        self.products_tree.heading('ID', text='ID')
        self.products_tree.heading('Name', text='Name')
        self.products_tree.heading('Price', text='Price')
        self.products_tree.heading('Stock', text='Stock')
        self.products_tree.heading('Category Name', text='Category Name')
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

        ttk.Button(controls_frame, text="DELETE ORDER (Transaction)", command=self.delete_order).pack(side='right',
                                                                                                      padx=20)

        columns = ('ID', 'Customer', 'Date', 'Status', 'Total')
        self.report_tree = ttk.Treeview(frame, columns=columns, show='headings')
        self.report_tree.heading('ID', text='ID')
        self.report_tree.heading('Customer', text='Customer')
        self.report_tree.heading('Date', text='Date')
        self.report_tree.heading('Status', text='Status')
        self.report_tree.heading('Total', text='Total')
        self.report_tree.pack(expand=True, fill='both')

    def setup_import_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Import")
        ttk.Label(frame, text="Expected JSON: [{'category': 'Name', 'name': 'Prod', 'price': 10, 'stock': 5}]").pack(
            pady=10)
        ttk.Button(frame, text="Import JSON Data", command=self.import_json).pack(pady=20)

    def refresh_dropdowns(self):
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT customer_id, first_name, last_name FROM customers")
            customers = cursor.fetchall()
            self.customer_map = {f"{c[1]} {c[2]} (ID: {c[0]})": c[0] for c in customers}
            self.customer_combo['values'] = list(self.customer_map.keys())

            cursor.execute("SELECT product_id, name, stock_quantity FROM products")
            products = cursor.fetchall()
            self.product_map = {f"{p[1]} (Stock: {p[2]})": p[0] for p in products}
            self.product_combo['values'] = list(self.product_map.keys())

            cursor.close()
        except Exception as e:
            pass

    def create_order(self):
        try:
            cust_selection = self.customer_combo.get()
            prod_selection = self.product_combo.get()

            if not cust_selection or not prod_selection:
                messagebox.showwarning("Validation Error", "Select a customer and a product.")
                return

            c_id = self.customer_map.get(cust_selection)
            p_id = self.product_map.get(prod_selection)
            qty = int(self.quantity_entry.get())

            if qty <= 0:
                messagebox.showwarning("Validation Error", "Quantity must be greater than 0.")
                return

            order = Order(c_id, [{'product_id': p_id, 'quantity': qty}])
            order.save_transaction()
            messagebox.showinfo("Success", "Order Created!")

            self.quantity_entry.delete(0, tkinter.END)
            self.customer_combo.set('')
            self.product_combo.set('')

            self.load_products(None)
            self.refresh_dropdowns()
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def create_product(self):
        try:
            name = self.prod_name_entry.get()
            price = self.prod_price_entry.get()
            stock = self.prod_stock_entry.get()
            cat_name = self.prod_cat_entry.get()

            category = Category(cat_name)
            category.save()

            product = Product(name, price, stock, category.category_id)
            product.save()
            messagebox.showinfo("Success", "Product Added!")

            self.prod_name_entry.delete(0, tkinter.END)
            self.prod_price_entry.delete(0, tkinter.END)
            self.prod_stock_entry.delete(0, tkinter.END)
            self.prod_cat_entry.delete(0, tkinter.END)

            self.load_products(None)
            self.refresh_dropdowns()
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def create_customer(self):
        first = self.cust_first_entry.get()
        last = self.cust_last_entry.get()
        email = self.cust_email_entry.get()

        try:
            customer = Customer(first, last, email)
            customer.save()
            messagebox.showinfo("Success", "Customer Added!")

            self.cust_first_entry.delete(0, tkinter.END)
            self.cust_last_entry.delete(0, tkinter.END)
            self.cust_email_entry.delete(0, tkinter.END)
            self.load_customers(None)
            self.refresh_dropdowns()
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_product_stock(self):
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a product first.")
            return

        product_id = self.products_tree.item(selected)['values'][0]

        quantity = simpledialog.askinteger("Restock", "Enter quantity to add:", parent=self.root, minvalue=1)

        if quantity:
            try:
                Product.add_stock(product_id, quantity)
                messagebox.showinfo("Success", "Stock updated.")
                self.load_products(None)
                self.refresh_dropdowns()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def update_order_status(self):
        selected_item = self.report_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select an order.")
            return

        order_id = self.report_tree.item(selected_item)['values'][0]
        try:
            Order.update_status(order_id, self.status_var.get())
            self.load_report(None)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_order(self):
        selected_item = self.report_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Select an order to delete.")
            return

        order_id = self.report_tree.item(selected_item)['values'][0]

        if messagebox.askyesno("Confirm", f"Delete Order {order_id}? Items will return to stock."):
            try:
                Order.delete_transaction(order_id)
                messagebox.showinfo("Success", "Order Deleted & Stock Returned.")
                self.load_report(None)
                self.load_products(None)
                self.refresh_dropdowns()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def load_products(self, frame):
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        try:
            connection = DatabaseConnection.get_connection()
            if not connection: return
            cursor = connection.cursor()

            query = """
                SELECT p.product_id, p.name, p.price, p.stock_quantity, c.name 
                FROM products p 
                LEFT JOIN categories c ON p.category_id = c.category_id
            """
            cursor.execute(query)

            for row in cursor.fetchall():
                self.products_tree.insert('', 'end', values=row)
            cursor.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def load_customers(self, frame):
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)
        try:
            connection = DatabaseConnection.get_connection()
            if not connection: return
            cursor = connection.cursor()
            cursor.execute("SELECT customer_id, first_name, last_name, email FROM customers")
            for row in cursor.fetchall():
                self.customers_tree.insert('', 'end', values=row)
            cursor.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def load_report(self, frame):
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)
        try:
            connection = DatabaseConnection.get_connection()
            if not connection: return
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM view_order_summary ORDER BY order_id DESC")
            for row in cursor.fetchall():
                self.report_tree.insert('', 'end', values=row)
            cursor.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def import_json(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not filepath: return
        try:
            with open(filepath, 'r') as file:
                data = json.load(file)

            if not isinstance(data, list):
                raise ValueError("JSON must contain a list.")

            count = 0
            for item in data:
                required_keys = ['category', 'name', 'price', 'stock']
                if not all(key in item for key in required_keys):
                    continue

                category = Category(item['category'])
                category.save()

                product = Product(item['name'], item['price'], item['stock'], category.category_id)
                product.save()
                count += 1

            messagebox.showinfo("Success", f"Imported {count} items.")
            self.load_products(None)
            self.refresh_dropdowns()
        except Exception as e:
            messagebox.showerror("Import Error", str(e))