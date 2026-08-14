import sqlite3 as sq
import pandas as pd

# Establising the connection
try:
    print(f"Connecting with cartiq_db")
    cartiq_conn = sq.connect("cartiq.db")
    print(f"Sucessful connection!!")
except Exception:
    print(f"Connection was not successful due to {Exception} !!.")

# Setting up the cursor
cursor_db = cartiq_conn.cursor()

# Create table
cursor_db.execute(
    """
    CREATE TABLE IF NOT EXISTS orders(
        order_id INTEGER UNIQUE NOT NULL,
        user_id INTEGER,
        eval_set TEXT,
        order_number INTEGER,
        order_dow INTEGER,
        order_hour_of_day INTEGER,
        days_since_prior_order INTEGER
    )
""")

cursor_db.execute(
    """
    CREATE TABLE IF NOT EXISTS products(
        product_id INTEGER NOT NULL,
        product_name TEXT,
        aisle_id INTEGER,
        department_id INTEGER
    )
""")

cursor_db.execute(
    """
    CREATE TABLE IF NOT EXISTS aisle(
        aisle_id INTEGER,
        aisle TEXT
    )
""")

cursor_db.execute(
    """
    CREATE TABLE IF NOT EXISTS departments(
        department_id INTEGER,
        department TEXT
    )
""")

cursor_db.execute(
    """
        CREATE TABLE IF NOT EXISTS prior_product_orders(
        order_id INTEGER,
        product_id INTEGER,
        add_to_cart INTEGER,
        reordered INTEGER
    )
"""
)

#reading files and feed into database

orders_df = pd.read_csv("/Users/abhijeetsinghparihar/Desktop/Projects/Supply Chain Project/CartIQ/data/raw/orders.csv", nrows=500)
products_df = pd.read_csv("/Users/abhijeetsinghparihar/Desktop/Projects/Supply Chain Project/CartIQ/data/raw/products.csv", nrows=500)
departments_df = pd.read_csv("//Users/abhijeetsinghparihar/Desktop/Projects/Supply Chain Project/CartIQ/data/raw/departments.csv")
aisle_df = pd.read_csv("/Users/abhijeetsinghparihar/Desktop/Projects/Supply Chain Project/CartIQ/data/raw/aisles.csv", nrows=500)
prior_products_order_df = pd.read_csv("//Users/abhijeetsinghparihar/Desktop/Projects/Supply Chain Project/CartIQ/data/raw/order_products_prior.csv", nrows=500)


try:
    print(f"\nReading 500 rows from orders.csv:-")
    orders_df.to_sql("orders", cartiq_conn, if_exists='replace', index=False)
    products_df.to_sql("products", cartiq_conn, if_exists='replace', index=False)
    aisle_df.to_sql("aisle", cartiq_conn, if_exists='replace', index=False)
    departments_df.to_sql("departments", cartiq_conn, if_exists='replace', index=False)
    prior_products_order_df.to_sql("prior_product_orders", cartiq_conn, if_exists='replace', index=False)
    print(f"Data was successfully fetched.")
except Exception:
    print(f"The data was not fetched due to {Exception}.")

print(pd.read_sql_query('SELECT * FROM orders LIMIT 5', cartiq_conn))
print(pd.read_sql_query('SELECT * FROM products LIMIT 5', cartiq_conn))
print(pd.read_sql_query('SELECT * FROM prior_product_orders LIMIT 5', cartiq_conn))
print(pd.read_sql_query('SELECT * FROM departments LIMIT 5', cartiq_conn))
print(pd.read_sql_query('SELECT * FROM aisle LIMIT 5', cartiq_conn))


#close the connection
cartiq_conn.close()
print("\nConnetion is closed!!")
