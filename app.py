from flask import Flask
import psycopg
from dotenv import load_dotenv
import os
app = Flask(__name__)

# with psycopg.connect("dbname= user=") as conn:
#     with conn.cursor() as cur:

# # connection is closed here.

load_dotenv()


USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")
DBURI = '''postgresql://postgres:@localhost:5432/merch'''
# Connect to the database
try:
    conn = psycopg.connect(host=HOST, user=USER, password=PASSWORD, port=PORT, dbname=DBNAME)
    print("Connection successful!")
    
    # Example query

    # # Close the cursor and connection
    # cursor.close()
    # connection.close()
    # print("Connection closed.")

except Exception as e:
    print(f"Failed to connect: {e}")

# conn = sqlite3.connect('undercroft_manager.db')

cur = conn.cursor()
cur.execute("SELECT NOW();")
result = cur.fetchone()
print("Current Time:", result)
# with open('schema.sql', 'r') as f:
#     schema = f.read()
#     cur.execute(schema)

record = cur.execute('''INSERT INTO prop (name, description, categoryID, isBroken, locationID, photoPath)
            VALUES (?, ?, ?, ?, ?, ?)
            RETURNING propID;''', ('Sword', 'Odyssiad prop', 1, 0, 1, '')).fetchone()
conn.commit()
print(record)
select_query = '''SELECT * FROM props WHERE name = %s''', ['Sword']
record = cur.execute(select_query).fetchone() # this is how in version 3 you do things

print(record)