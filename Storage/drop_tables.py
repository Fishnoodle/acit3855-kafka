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
            DROP TABLE restaurant, delivery
            ''')

connection.commit()
connection.close()


