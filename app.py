import sqlite3
from flask import Flask
import psycopg
from dotenv import load_dotenv
import os
app = Flask(__name__)

# with psycopg.connect("dbname= user=") as conn:
#     with conn.cursor() as cur:

# # connection is closed here.

load_dotenv()
# url = os.environ.get("DATABASE_URL")
# conn = psycopg.connect(url)
conn = sqlite3.connect('undercroft_manager.db')
cur = conn.cursor()
with open('schema.sql', 'r') as f:
    schema = f.read()
    cur.execute(schema)

record = cur.execute('''INSERT INTO prop (name, description, categoryID, isBroken, locationID, photoPath)
            VALUES (?, ?, ?, ?, ?, ?)
            RETURNING propID;''', ('Sword', 'Odyssiad prop', 1, 0, 1, '')).fetchone()
conn.commit()
print(record)
select_query = '''SELECT * FROM props WHERE name = %s''', ['Sword']
record = cur.execute(select_query).fetchone() # this is how in version 3 you do things

print(record)