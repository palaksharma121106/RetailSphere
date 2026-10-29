# RetailSphere - SQLite builder (for Streamlit Community Cloud)
# Same schema + same Faker data logic as schema.sql / generate_data.py,
# but writes straight into a single file: retailsphere.db
# (Streamlit Cloud has no MySQL server, SQLite needs none.)
#
# Run locally:  pip install faker && python build_sqlite.py

import os
import random
import sqlite3
from datetime import datetime, timedelta

from faker import Faker

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "retailsphere.db")

# ── Config (same as generate_data.py) ────────────────────
NUM_CUSTOMERS = 5000
NUM_ORDERS = 10000
NUM_PRODUCTS = 200
NUM_SUPPLIERS = 50
NUM_WAREHOUSES = 10

CATEGORIES = [
    ("Electronics", "Technology"), ("Clothing", "Fashion"),
    ("Groceries", "Food"), ("Furniture", "Home"),
    ("Books", "Education"), ("Sports", "Fitness"),
    ("Toys", "Kids"), ("Beauty", "Personal Care"),
    ("Automotive", "Vehicles"), ("Garden", "Outdoor"),
]
STATUSES = ["pending", "processing", "shipped", "delivered", "cancelled"]
STATUS_WEIGHTS = [5, 10, 20, 60, 5]
STATES = ["Rajasthan", "Maharashtra", "Karnataka", "Delhi", "Gujarat",
          "Tamil Nadu", "Uttar Pradesh", "West Bengal", "Punjab", "Telangana"]
CITIES = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad",
          "Pune", "Jaipur", "Kolkata", "Ahmedabad", "Lucknow"]
PRODUCT_NAMES = [
    "Smart TV", "Laptop", "Headphones", "Keyboard", "Mouse", "Charger",
    "T-Shirt", "Jeans", "Sneakers", "Jacket", "Dress", "Kurta",
    "Rice 5kg", "Dal 1kg", "Oil 1L", "Sugar 2kg", "Tea 500g",
    "Sofa", "Bed Frame", "Dining Table", "Bookshelf", "Wardrobe",
    "Cricket Bat", "Football", "Yoga Mat", "Dumbbells",
    "Shampoo", "Face Wash", "Moisturiser", "Lipstick",
]

# MySQL -> SQLite changes: AUTO_INCREMENT -> INTEGER PRIMARY KEY,
# DECIMAL -> REAL, ENUM -> TEXT + CHECK, and explicit indexes
# (MySQL InnoDB makes FK indexes automatically, SQLite does not).
SCHEMA = """
CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT
);
CREATE TABLE suppliers (
    supplier_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    country TEXT,
    rating REAL,
    contact_email TEXT
);
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category_id INTEGER REFERENCES categories(category_id),
    supplier_id INTEGER REFERENCES suppliers(supplier_id),
    price REAL
);
CREATE TABLE warehouses (
    warehouse_id INTEGER PRIMARY KEY,
    city TEXT,
    state TEXT,
    capacity INTEGER
);
CREATE TABLE inventory (
    inventory_id INTEGER PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    warehouse_id INTEGER REFERENCES warehouses(warehouse_id),
    quantity INTEGER DEFAULT 0,
    reorder_level INTEGER DEFAULT 50
);
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    city TEXT,
    state TEXT,
    joined_date TEXT
);
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    order_date TEXT,
    status TEXT CHECK (status IN ('pending','processing','shipped','delivered','cancelled')),
    total_amount REAL
);
CREATE TABLE order_items (
    item_id INTEGER PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER,
    unit_price REAL
);
CREATE INDEX idx_orders_date      ON orders(order_date);
CREATE INDEX idx_orders_customer  ON orders(customer_id);
CREATE INDEX idx_items_order      ON order_items(order_id);
CREATE INDEX idx_items_product    ON order_items(product_id);
CREATE INDEX idx_products_supplier ON products(supplier_id);
CREATE INDEX idx_inventory_product ON inventory(product_id);
"""


def rand_date(start_year, end_year):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))


def build(db_path=DB_PATH):
    random.seed(42)
    Faker.seed(42)
    fake = Faker("en_IN")

    if os.path.exists(db_path):
        os.remove(db_path)
    con = sqlite3.connect(db_path)
    con.executescript(SCHEMA)

    con.executemany("INSERT INTO categories VALUES (?,?,?)",
                    [(i, n, d) for i, (n, d) in enumerate(CATEGORIES, 1)])

    suppliers = []
    for i in range(1, NUM_SUPPLIERS + 1):
        suppliers.append((i, fake.company().replace("'", ""),
                          random.choice(["India", "China", "USA", "Germany", "Japan"]),
                          round(random.uniform(3.0, 5.0), 2), fake.company_email()))
    con.executemany("INSERT INTO suppliers VALUES (?,?,?,?,?)", suppliers)

    products = []
    for i in range(1, NUM_PRODUCTS + 1):
        products.append((i, (random.choice(PRODUCT_NAMES) + f" #{i}").replace("'", ""),
                         random.randint(1, len(CATEGORIES)),
                         random.randint(1, NUM_SUPPLIERS),
                         round(random.uniform(50, 50000), 2)))
    con.executemany("INSERT INTO products VALUES (?,?,?,?,?)", products)

    con.executemany("INSERT INTO warehouses VALUES (?,?,?,?)",
                    [(i, CITIES[i - 1], STATES[i - 1], random.randint(10000, 100000))
                     for i in range(1, NUM_WAREHOUSES + 1)])

    inventory, inv_id = [], 1
    for p in range(1, NUM_PRODUCTS + 1):
        for w in random.sample(range(1, NUM_WAREHOUSES + 1), k=random.randint(2, 5)):
            inventory.append((inv_id, p, w, random.randint(0, 5000), random.randint(20, 200)))
            inv_id += 1
    con.executemany("INSERT INTO inventory VALUES (?,?,?,?,?)", inventory)

    customers = []
    for i in range(1, NUM_CUSTOMERS + 1):
        customers.append((i, fake.name().replace("'", ""),
                          f"user{i}_{fake.user_name()}@{fake.free_email_domain()}",
                          fake.city().replace("'", ""), random.choice(STATES),
                          rand_date(2020, 2024).strftime("%Y-%m-%d")))
    con.executemany("INSERT INTO customers VALUES (?,?,?,?,?,?)", customers)

    orders, items, item_id = [], [], 1
    for o in range(1, NUM_ORDERS + 1):
        cust_id = random.randint(1, NUM_CUSTOMERS)
        o_date = rand_date(2022, 2025)
        status = random.choices(STATUSES, STATUS_WEIGHTS)[0]
        total = 0
        for _ in range(random.randint(1, 5)):
            qty = random.randint(1, 10)
            unit_price = round(random.uniform(50, 10000), 2)
            total += qty * unit_price
            items.append((item_id, o, random.randint(1, NUM_PRODUCTS), qty, unit_price))
            item_id += 1
        orders.append((o, cust_id, o_date.strftime("%Y-%m-%d %H:%M:%S"), status, round(total, 2)))
    con.executemany("INSERT INTO orders VALUES (?,?,?,?,?)", orders)
    con.executemany("INSERT INTO order_items VALUES (?,?,?,?,?)", items)

    con.commit()
    con.close()


if __name__ == "__main__":
    build()
    con = sqlite3.connect(DB_PATH)
    for t in ["customers", "orders", "order_items", "products", "inventory", "suppliers", "warehouses"]:
        print(f"{t:12s}: {con.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]:,}")
    con.close()
    print("Built", DB_PATH)