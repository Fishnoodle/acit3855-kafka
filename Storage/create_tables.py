import mysql.connector


connection = mysql.connector.connect(
        host="bcitacit3855.eastus.cloudapp.azure.com",
        port="3306",
        user="root",
        password="password",
        database="request"
        )

conn = connection.cursor()

conn.execute('''
        CREATE TABLE restaurant
        (id INTEGER NOT NULL AUTO_INCREMENT,
        order_id VARCHAR(250) NOT NULL,
        customer_id VARCHAR(250) NOT NULL,
        item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price INTEGER NOT NULL,
        time_stamp VARCHAR(250) NOT NULL,
        date_created VARCHAR(250) NOT NULL,
        trace_id VARCHAR(250) NOT NULL,
        CONSTRAINT restaurant_request_pk PRIMARY KEY (id))
        ''')


conn.execute('''
        CREATE TABLE delivery
        (id INTEGER NOT NULL AUTO_INCREMENT,
        order_id VARCHAR(250) NOT NULL,
        item_id INTEGER NOT NULL,
        price INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        pickup_address VARCHAR(250) NOT NULL,
        order_address VARCHAR(250) NOT NULL,
        date_created VARCHAR(250) NOT NULL,
        trace_id VARCHAR(250) NOT NULL,
        CONSTRAINT delivery_request_pk PRIMARY KEY (id))
        ''')

connection.commit()
connection.close()
