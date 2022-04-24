import sqlite3

connection = sqlite3.connect('stats.sqlite')

conn = connection.cursor()
conn.execute('''
            CREATE TABLE stats
            (id INTEGER PRIMARY KEY ASC,
            num_orders_total INTEGER NOT NULL,
            max_quantity INTEGER NOT NULL,
            min_quantity INTEGER NOT NULL,
            num_customers_total INTEGER NOT NULL,
            last_updated VARCHAR(100) NOT NULL)
            ''')

connection.commit()
connection.close()