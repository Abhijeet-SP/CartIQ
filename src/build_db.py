from pathlib import Path
import sqlite3 as sq
import pandas as pd

# file path
data_file = Path(__file__).resolve().parent.parent/'data'

# Establising the connection
try:
    print(f"Connecting with cartiq_db")
    cartiq_conn = sq.connect(data_file/ "cartiq.db")
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
        order_dow INTEGER,
        order_hour_of_day INTEGER,
        days_since_prior_order INTEGER,
        order_number INTEGER,
        product_id INTEGER,
        add_to_cart_order INTEGER,
        reordered INTEGER,
        product_name TEXT,
        department_id INTEGER,
        department TEXT
    )
""")

# reading files and feed into database
orders_df = pd.read_csv(data_file/ 'processed'/ "master_orders.csv")

# writing the data into the database
try:
    print(f"\nReading rows from orders.csv:-")
    orders_df.to_sql("orders", cartiq_conn, if_exists='replace', index=False)
    print(f"Data was successfully wrote.")
except Exception:
    print(f"The data was not fetched due to {Exception}.")

# checking the written data 
print(pd.read_sql_query('SELECT * FROM orders LIMIT 5', cartiq_conn))

#close the connection
cartiq_conn.close()
print("\nConnetion is closed!!")
