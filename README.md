# Store Manager System D2

## Project Information

| Field | Value                                       |
|------|---------------------------------------------|
| Project Name | Store Manager System (D2)                   |
| Author | Sebastian Janíček                           |
| Contact | janicek@spsejecna.cz sebikjanecek@gmail.com |
| School | SPŠE Ječná                                  |
| Context | School Project (Subject: PV)                |

---

## 1. Requirement Specification

### 1.1 Business Requirements

The objective is to digitize the inventory and order management process for a small retail business.  
The system replaces manual paper records with a robust database application to ensure data integrity and stock accuracy.

### 1.2 Functional Requirements

- **Inventory Management:** Add, update, and delete products and categories.
- **Customer Management:** Register and manage customer details.
- **Order Processing:** Create orders for customers. Purchased items are automatically deducted from stock.
- **Transaction Integrity:**  
  Order creation consists of multiple steps (Header → Items → Stock deduction) and must be atomic.
- **Status Management:**  
  Order statuses: `PENDING`, `SHIPPED`, `PAID`, `CANCELLED`.  
  Cancelling an order returns items to stock.
- **Reporting:** Generate order summaries with calculated totals.
- **Data Import / Export:** Import via JSON, export to CSV.

### 1.3 Non-Functional Requirements

- Platform: Windows PC (School Desktop)
- Language: Python 3.x
- GUI Framework: Tkinter
- Database: MySQL
- Design Pattern: D2 – Active Record

---

## 2. System Architecture

Layered architecture combined with the Active Record pattern.

### 2.1 High-Level Architecture

```text
[ User Interface Layer (Tkinter) ]
           |
           v
[ Business Logic / Data Layer (Active Record Models) ]
           |
           v
[ Infrastructure Layer (Database Connection Singleton) ]
           |
           v
[ MySQL Database Server ]
```

### 2.2 Design Patterns Used

**Active Record (D2)**  
Each table (`products`, `orders`, `customers`) has a Python class in `src/models/`.

**Singleton**  
Implemented in `src/database/connection.py` to share one DB connection.

### 2.3 Libraries & Dependencies

- Python Standard Library: tkinter, configparser, json, csv, os, sys, re
- External: mysql-connector-python

---

## 3. Database Design

### 3.1 Relationships

- Categories 1:N Products  
- Customers 1:N Orders  
- Orders M:N Products (via order_items)

### 3.2 Database Schema

#### categories

| Column | Type | Constraints | Description |
|------|------|------------|------------|
| category_id | INT | PK, Auto Inc | Unique ID |
| name | VARCHAR(100) | UNIQUE, NOT NULL | Category name |
| is_active | TINYINT(1) | Default 1 | Soft delete |

#### products

| Column | Type | Constraints | Description |
|------|------|------------|------------|
| product_id | INT | PK, Auto Inc | Unique ID |
| name | VARCHAR(200) | NOT NULL | Product name |
| price | DECIMAL(10,2) | NOT NULL | Price |
| stock_quantity | INT | Default 0 | Stock |
| category_id | INT | FK | Category |

#### customers

| Column | Type | Constraints | Description |
|------|------|------------|------------|
| customer_id | INT | PK, Auto Inc | Unique ID |
| first_name | VARCHAR(50) | NOT NULL | First name |
| last_name | VARCHAR(50) | NOT NULL | Last name |
| email | VARCHAR(100) | UNIQUE | Email |

#### orders

| Column | Type | Constraints | Description |
|------|------|------------|------------|
| order_id | INT | PK, Auto Inc | Unique ID |
| customer_id | INT | FK | Customer |
| order_date | DATETIME | Default NOW | Created |
| status | ENUM | Constraint | Order status |

#### order_items

| Column | Type | Constraints | Description |
|------|------|------------|------------|
| item_id | INT | PK, Auto Inc | Unique ID |
| order_id | INT | FK | Order |
| product_id | INT | FK | Product |
| quantity | INT | NOT NULL | Quantity |
| unit_price | DECIMAL | NOT NULL | Price |

---

## 4. Configuration

`config/settings.ini`

```ini
[mysql]
host = localhost
user = root
password =
database = 
port = 3306
```

---

## 5. Installation & Execution

- Install Python 3.x
- Run MySQL Server
- Install dependency:
  ```bash
  pip install mysql-connector-python
  ```
- Run:
  ```bash
  python src/main.py
  ```

---

## 6. Program Behavior

### Creating an Order
- Select customer, product, quantity
- Transaction validates stock
- Order + items created
- Stock updated

### Cancelling an Order
- Status set to `CANCELLED`
- Items returned to stock

---

## 7. Import & Export

### Import (JSON)

```json
[
  {
    "category": "Electronics",
    "name": "Smartphone",
    "price": 15000,
    "stock": 10
  }
]
```

### Export
- Products
- Customers
- Order summary

---

## 8. Error Handling

| Error | Reaction |
|-----|---------|
| DB Connection | Critical popup |
| Validation | Warning |
| Stock | Rollback |
| FK Constraint | User warning |
| Import | Skip invalid |

---

## 9. Testing

- Installation & DB creation: PASS  
- Core features: PASS  
- Error handling: PASS  


