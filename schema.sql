-- ═══════════════════════════════════════════════
--  RetailSphere — Retail Supply Chain Database
--  Schema: 8 tables, normalized to 3NF
-- ═══════════════════════════════════════════════

CREATE DATABASE IF NOT EXISTS retailsphere;
USE retailsphere;

-- 1. Categories
CREATE TABLE categories (
    category_id   INT PRIMARY KEY AUTO_INCREMENT,
    name          VARCHAR(100) NOT NULL,
    department    VARCHAR(100)
);

-- 2. Suppliers
CREATE TABLE suppliers (
    supplier_id   INT PRIMARY KEY AUTO_INCREMENT,
    name          VARCHAR(150) NOT NULL,
    country       VARCHAR(100),
    rating        DECIMAL(3,2),
    contact_email VARCHAR(150)
);

-- 3. Products
CREATE TABLE products (
    product_id    INT PRIMARY KEY AUTO_INCREMENT,
    name          VARCHAR(200) NOT NULL,
    category_id   INT,
    supplier_id   INT,
    price         DECIMAL(10,2),
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

-- 4. Warehouses
CREATE TABLE warehouses (
    warehouse_id  INT PRIMARY KEY AUTO_INCREMENT,
    city          VARCHAR(100),
    state         VARCHAR(100),
    capacity      INT
);

-- 5. Inventory
CREATE TABLE inventory (
    inventory_id  INT PRIMARY KEY AUTO_INCREMENT,
    product_id    INT,
    warehouse_id  INT,
    quantity      INT DEFAULT 0,
    reorder_level INT DEFAULT 50,
    FOREIGN KEY (product_id)  REFERENCES products(product_id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id)
);

-- 6. Customers
CREATE TABLE customers (
    customer_id   INT PRIMARY KEY AUTO_INCREMENT,
    name          VARCHAR(150) NOT NULL,
    email         VARCHAR(150) UNIQUE,
    city          VARCHAR(100),
    state         VARCHAR(100),
    joined_date   DATE
);

-- 7. Orders
CREATE TABLE orders (
    order_id      INT PRIMARY KEY AUTO_INCREMENT,
    customer_id   INT,
    order_date    DATETIME,
    status        ENUM('pending','processing','shipped','delivered','cancelled'),
    total_amount  DECIMAL(12,2),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- 8. Order Items
CREATE TABLE order_items (
    item_id       INT PRIMARY KEY AUTO_INCREMENT,
    order_id      INT,
    product_id    INT,
    quantity      INT,
    unit_price    DECIMAL(10,2),
    FOREIGN KEY (order_id)   REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);