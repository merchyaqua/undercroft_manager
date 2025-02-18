from dotenv import load_dotenv
import psycopg
import os
from psycopg.rows import dict_row

def connect():
    load_dotenv()
    USER = os.getenv("user")
    PASSWORD = os.getenv("password")
    HOST = os.getenv("host")
    PORT = os.getenv("port")
    DBNAME = os.getenv("dbname")
    DBURI = '''postgresql://postgres:@localhost:5432/merch'''
    # Connect to the database
    try:
        conn = psycopg.connect(host=HOST, user=USER, password=PASSWORD, port=PORT, dbname=DBNAME, row_factory=dict_row)
        print("Connection successful!")
        conn.autocommit = True

        return conn
        # Example query

        # # Close the cursor and connection
        # cursor.close()
        # connection.close()
        # print("Connection closed.")

    except Exception as e:
        print(f"Failed to connect: {e}")

def test_cursor(cur):
    cur.execute("SELECT NOW();")
    result = cur.fetchone()
    print("Current Time:", result)
    # with open('schema.sql', 'r') as f:
    #     schema = f.read()
    #     cur.execute(schema)

    record = cur.execute('''INSERT INTO prop (name, description, categoryID, isBroken, locationID, photoPath)
                VALUES (%s,%s,%s,%s,%s,%s)
                RETURNING propID;''', ('Sword', 'Odyssiad prop', 1, False, 1, 'test')).fetchone()
    print(record)
    select_query = '''SELECT name FROM prop WHERE name = %s''', ['Sword']
    record = cur.execute(select_query).fetchone() # this is how in version 3 you do things

    print(record)

# test_cursor(cur)