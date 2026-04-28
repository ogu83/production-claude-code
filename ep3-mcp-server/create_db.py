"""create_db.py — Bootstrap the sample SQLite database.

Creates data/sample.db with two tables:
  products  — product catalog (id, name, category, price, stock_qty)
  orders    — order history  (id, product_id, quantity, order_date, status)

Run once before starting the MCP server:
    python create_db.py

Re-run to reset the database to a clean demo state.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "sample.db"


SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    category    TEXT NOT NULL,
    price       REAL NOT NULL,
    stock_qty   INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    id          INTEGER PRIMARY KEY,
    product_id  INTEGER NOT NULL REFERENCES products(id),
    quantity    INTEGER NOT NULL,
    order_date  TEXT NOT NULL,   -- ISO 8601: YYYY-MM-DD
    status      TEXT NOT NULL    -- pending | shipped | delivered | returned
);
"""

PRODUCTS = [
    # (name, category, price, stock_qty)
    ("Wireless Headphones",    "Electronics",  89.99,  42),
    ("Mechanical Keyboard",    "Electronics", 129.00,  18),
    ("USB-C Hub 7-Port",       "Electronics",  34.50,   7),
    ("Laptop Stand Aluminium", "Electronics",  49.95,  55),
    ("Webcam 1080p",           "Electronics",  64.00,   3),
    ("Desk Lamp LED",          "Office",       28.00,  90),
    ("Ergonomic Chair Lumbar", "Office",      199.00,  12),
    ("Whiteboard 90x60cm",     "Office",       45.00,   6),
    ("Sticky Notes 12-pack",   "Office",        6.50, 200),
    ("Cable Management Kit",   "Office",       14.99,  33),
    ("Python Crash Course",    "Books",        29.99,  60),
    ("Clean Code",             "Books",        34.00,  41),
    ("Designing Data Systems", "Books",        44.95,  22),
    ("The Pragmatic Programmer","Books",       39.99,  15),
    ("Standing Desk Mat",      "Wellness",     49.00,  28),
    ("Blue Light Glasses",     "Wellness",     22.00,  50),
    ("Posture Corrector",      "Wellness",     18.50,   9),
]

ORDERS = [
    # (product_id, quantity, order_date, status)
    (1,  1, "2025-01-03", "delivered"),
    (1,  2, "2025-01-15", "delivered"),
    (2,  1, "2025-01-08", "delivered"),
    (2,  1, "2025-02-01", "returned"),
    (3,  3, "2025-01-20", "delivered"),
    (4,  1, "2025-01-22", "delivered"),
    (5,  1, "2025-02-05", "shipped"),
    (5,  1, "2025-02-18", "pending"),
    (6,  2, "2025-01-10", "delivered"),
    (7,  1, "2025-01-28", "delivered"),
    (7,  1, "2025-02-10", "delivered"),
    (8,  1, "2025-02-14", "shipped"),
    (9,  5, "2025-01-05", "delivered"),
    (9, 10, "2025-02-20", "pending"),
    (10, 2, "2025-01-18", "delivered"),
    (11, 1, "2025-01-06", "delivered"),
    (11, 1, "2025-02-02", "delivered"),
    (12, 1, "2025-01-12", "delivered"),
    (13, 1, "2025-01-25", "delivered"),
    (13, 1, "2025-02-08", "returned"),
    (14, 1, "2025-02-12", "delivered"),
    (15, 1, "2025-01-30", "delivered"),
    (16, 2, "2025-02-03", "delivered"),
    (17, 1, "2025-02-15", "shipped"),
    (3,  1, "2025-02-22", "pending"),
    (1,  1, "2025-02-25", "pending"),
    (6,  1, "2025-02-26", "pending"),
    (12, 1, "2025-02-27", "pending"),
    (4,  2, "2025-02-28", "pending"),
    (11, 1, "2025-03-01", "pending"),
]


def create() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Drop existing tables so re-running gives a clean slate.
    cur.execute("DROP TABLE IF EXISTS orders")
    cur.execute("DROP TABLE IF EXISTS products")
    conn.commit()

    cur.executescript(SCHEMA)

    cur.executemany(
        "INSERT INTO products (name, category, price, stock_qty) VALUES (?,?,?,?)",
        PRODUCTS,
    )
    cur.executemany(
        "INSERT INTO orders (product_id, quantity, order_date, status) VALUES (?,?,?,?)",
        ORDERS,
    )
    conn.commit()
    conn.close()

    print(f"Created {DB_PATH}")
    print(f"  {len(PRODUCTS)} products across {len({p[1] for p in PRODUCTS})} categories")
    print(f"  {len(ORDERS)} orders")
    print()
    print("Try these queries:")
    print("  SELECT * FROM products WHERE stock_qty < 10;")
    print("  SELECT category, SUM(price * stock_qty) AS inventory_value")
    print("    FROM products GROUP BY category ORDER BY inventory_value DESC;")
    print("  SELECT p.name, COUNT(o.id) AS order_count, SUM(o.quantity) AS units_sold")
    print("    FROM products p JOIN orders o ON p.id = o.product_id")
    print("    WHERE o.status = 'delivered' GROUP BY p.id ORDER BY units_sold DESC;")


if __name__ == "__main__":
    create()
