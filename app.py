from flask import Flask
import psycopg
from dotenv import load_dotenv
import os
app = Flask(__name__)

# with psycopg.connect("dbname= user=") as conn:
#     with conn.cursor() as cur:

# # connection is closed here.

load_dotenv()
url = os.environ.get("DATABASE_URL")
conn = psycopg.connect(url)
cur = conn.cursor()
# SQL Queries to set up tables
CREATE_QUERIES = [
    '''CREATE TABLE IF NOT EXISTS props (
        propID SERIAL PRIMARY KEY,
        name VARCHAR(50) NOT NULL,
        description TEXT,
        categoryID FOREIGN KEY,
        isBroken BOOL NOT NULL,
        locationID FOREIGN KEY,
        photoPath TEXT,


    )'''
]
insert_query = '''INSERT INTO props (name, description, categoryID, isBroken, locationID, photoPath)
            VALUES (%s, %s)
            RETURNING propID''', ('Sword', 'Odyssiad prop') # etc

record = cur.execute(insert_query).fetchone()
conn.commit()

select_query = '''SELECT * FROM props WHERE name = %s''', ['Sword']
record = cur.execute(select_query).fetchone() # this is how in version 3 you do things