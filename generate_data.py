# ═══════════════════════════════════════════════════════════
#  RetailSphere — Data Generator
#  Generates realistic retail data: 50,000 customers,
#  100,000+ orders, 500,000+ order items
#
#  Install: pip install faker mysql-connector-python
#  Run:     python generate_data.py
# ═══════════════════════════════════════════════════════════

import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker('en_IN')  # Indian locale
random.seed(42)

# ── Config ───────────────────────────────────────────────
NUM_CUSTOMERS  = 5000
NUM_ORDERS     = 10000
NUM_PRODUCTS   = 200
NUM_SUPPLIERS  = 50
NUM_WAREHOUSES = 10

CATEGORIES = [
    ("Electronics", "Technology"), ("Clothing", "Fashion"),
    ("Groceries", "Food"), ("Furniture", "Home"),
    ("Books", "Education"), ("Sports", "Fitness"),
    ("Toys", "Kids"), ("Beauty", "Personal Care"),
    ("Automotive", "Vehicles"), ("Garden", "Outdoor")
]

STATUSES = ['pending','processing','shipped','delivered','cancelled']
STATUS_WEIGHTS = [5, 10, 20, 60, 5]

STATES = ['Rajasthan','Maharashtra','Karnataka','Delhi','Gujarat',
          'Tamil Nadu','Uttar Pradesh','West Bengal','Punjab','Telangana']

# ── Helpers ──────────────────────────────────────────────
def rand_date(start_year=2022, end_year=2025):
    start = datetime(start_year, 1, 1)
    end   = datetime(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))

def fmt(d):
    return d.strftime('%Y-%m-%d %H:%M:%S')

# ── Generate SQL ─────────────────────────────────────────
lines = []
lines.append("USE retailsphere;")
lines.append("SET FOREIGN_KEY_CHECKS=0;")

# 1. Categories
lines.append("\n-- Categories")
for i, (name, dept) in enumerate(CATEGORIES, 1):
    lines.append(f"INSERT INTO categories VALUES ({i},'{name}','{dept}');")

# 2. Suppliers
lines.append("\n-- Suppliers")
for i in range(1, NUM_SUPPLIERS+1):
    name  = fake.company().replace("'","")
    cntry = random.choice(['India','China','USA','Germany','Japan'])
    rating= round(random.uniform(3.0, 5.0), 2)
    email = fake.company_email()
    lines.append(f"INSERT INTO suppliers VALUES ({i},'{name}','{cntry}',{rating},'{email}');")

# 3. Products
lines.append("\n-- Products")
PRODUCT_NAMES = [
    "Smart TV","Laptop","Headphones","Keyboard","Mouse","Charger",
    "T-Shirt","Jeans","Sneakers","Jacket","Dress","Kurta",
    "Rice 5kg","Dal 1kg","Oil 1L","Sugar 2kg","Tea 500g",
    "Sofa","Bed Frame","Dining Table","Bookshelf","Wardrobe",
    "Cricket Bat","Football","Yoga Mat","Dumbbells",
    "Shampoo","Face Wash","Moisturiser","Lipstick"
]
for i in range(1, NUM_PRODUCTS+1):
    name    = random.choice(PRODUCT_NAMES) + f" #{i}"
    name    = name.replace("'","")
    cat_id  = random.randint(1, len(CATEGORIES))
    sup_id  = random.randint(1, NUM_SUPPLIERS)
    price   = round(random.uniform(50, 50000), 2)
    lines.append(f"INSERT INTO products VALUES ({i},'{name}',{cat_id},{sup_id},{price});")

# 4. Warehouses
lines.append("\n-- Warehouses")
CITIES = ['Mumbai','Delhi','Bangalore','Chennai','Hyderabad',
          'Pune','Jaipur','Kolkata','Ahmedabad','Lucknow']
for i in range(1, NUM_WAREHOUSES+1):
    city  = CITIES[i-1]
    state = STATES[i-1]
    cap   = random.randint(10000, 100000)
    lines.append(f"INSERT INTO warehouses VALUES ({i},'{city}','{state}',{cap});")

# 5. Inventory
lines.append("\n-- Inventory")
inv_id = 1
for p in range(1, NUM_PRODUCTS+1):
    for w in random.sample(range(1, NUM_WAREHOUSES+1), k=random.randint(2,5)):
        qty     = random.randint(0, 5000)
        reorder = random.randint(20, 200)
        lines.append(f"INSERT INTO inventory VALUES ({inv_id},{p},{w},{qty},{reorder});")
        inv_id += 1

# 6. Customers
lines.append("\n-- Customers (50,000 rows)")
for i in range(1, NUM_CUSTOMERS+1):
    name  = fake.name().replace("'","")
    email = f"user{i}_{fake.user_name()}@{fake.free_email_domain()}"
    city  = fake.city().replace("'","")
    state = random.choice(STATES)
    date  = rand_date(2020, 2024).strftime('%Y-%m-%d')
    lines.append(f"INSERT INTO customers VALUES ({i},'{name}','{email}','{city}','{state}','{date}');")
    if i % 5000 == 0:
        print(f"  Customers: {i}/{NUM_CUSTOMERS}")

# 7. Orders + 8. Order Items
lines.append("\n-- Orders & Order Items (100K orders)")
item_id = 1
for o in range(1, NUM_ORDERS+1):
    cust_id = random.randint(1, NUM_CUSTOMERS)
    o_date  = rand_date(2022, 2025)
    status  = random.choices(STATUSES, STATUS_WEIGHTS)[0]
    
    # 1-5 items per order
    items = []
    total = 0
    for _ in range(random.randint(1, 5)):
        prod_id   = random.randint(1, NUM_PRODUCTS)
        qty       = random.randint(1, 10)
        unit_price= round(random.uniform(50, 10000), 2)
        total    += qty * unit_price
        items.append((item_id, o, prod_id, qty, unit_price))
        item_id += 1

    total = round(total, 2)
    lines.append(f"INSERT INTO orders VALUES ({o},{cust_id},'{fmt(o_date)}','{status}',{total});")
    for it in items:
        lines.append(f"INSERT INTO order_items VALUES {it};")

    if o % 10000 == 0:
        print(f"  Orders: {o}/{NUM_ORDERS}")

lines.append("\nSET FOREIGN_KEY_CHECKS=1;")
lines.append("SELECT 'Data generation complete!' AS status;")

# Write to file
with open('data.sql', 'w') as f:
    f.write('\n'.join(lines))

print("\n✅ data.sql generated successfully!")
print(f"   Customers  : {NUM_CUSTOMERS:,}")
print(f"   Orders     : {NUM_ORDERS:,}")
print(f"   Products   : {NUM_PRODUCTS:,}")
print(f"   Order Items: ~{NUM_ORDERS * 3:,} (avg 3/order)")
print("\nNext step: mysql -u root -p < data.sql")