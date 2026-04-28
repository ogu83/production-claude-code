# data/

This directory contains generated assets — do not commit.

## Setup

Run once before starting the MCP server:

```bash
cd ep3-mcp-server
python create_db.py
```

This creates `data/sample.db` with:
- `products` table — 17 products across 4 categories (Electronics, Office, Books, Wellness)
- `orders` table — 30 orders with statuses: pending / shipped / delivered / returned

## Sample queries

```sql
-- Low-stock products
SELECT name, stock_qty FROM products WHERE stock_qty < 10 ORDER BY stock_qty;

-- Inventory value by category
SELECT category, SUM(price * stock_qty) AS inventory_value
FROM products GROUP BY category ORDER BY inventory_value DESC;

-- Best-selling products (by units delivered)
SELECT p.name, COUNT(o.id) AS orders, SUM(o.quantity) AS units_sold
FROM products p JOIN orders o ON p.id = o.product_id
WHERE o.status = 'delivered'
GROUP BY p.id ORDER BY units_sold DESC LIMIT 5;

-- Order status breakdown
SELECT status, COUNT(*) AS count FROM orders GROUP BY status;
```

## Files the read_file tool can access

Any `.txt`, `.json`, `.md`, or `.sql` file placed in this directory is readable
via the `read_file` MCP tool. Place reference data, schema files, or lookup
tables here for Claude to read on demand.
