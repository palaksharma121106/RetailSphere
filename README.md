# RetailSphere — Large-Scale Retail Supply Chain Analytics

A Walmart-inspired relational database system modelling retail supply chain operations at scale.

## Dataset Size
| Table | Rows |
|---|---|
| Customers | 5,000 |
| Orders | 10,000 |
| Order Items | ~300,000 |
| Products | 200 |
| Inventory | ~2,500 |

## Schema
```
customers → orders → order_items → products → categories
                                 → products → suppliers
inventory → products
inventory → warehouses
```

## How to Run

### Step 1 — Install requirements
```bash
pip install faker mysql-connector-python
```

### Step 2 — Create schema
```bash
mysql -u root -p < schema.sql
```

### Step 3 — Generate & load data
```bash
python generate_data.py
mysql -u root -p < data.sql
```

### Step 4 — Run analytics
```bash
mysql -u root -p retailsphere < analytics.sql
```

## Key Features
- RFM Customer Segmentation (Gold / Silver / Bronze tiers)
- Low inventory alerts with reorder quantity calculation
- Supplier performance scoring
- Monthly revenue trends with window functions (running totals)
- State-wise sales analytics
- Optimized with indexes on foreign keys and order_date

## Tech Stack
MySQL 8.0 · Python 3.x · Faker library