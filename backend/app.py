from flask import Flask, debughelpers
from flask import render_template, request, redirect
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
import os
import json
app = Flask(__name__)

# with psycopg.connect("dbname= user=") as conn:
#     with conn.cursor() as cur:
# # connection is closed here.
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
        return conn
        # Example query

        # # Close the cursor and connection
        # cursor.close()
        # connection.close()
        # print("Connection closed.")

    except Exception as e:
        print(f"Failed to connect: {e}")

# conn = sqlite3.connect('undercroft_manager.db')


conn = connect()
cur = conn.cursor()


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
    conn.commit()
    print(record)
    select_query = '''SELECT name FROM prop WHERE name = %s''', ['Sword']
    record = cur.execute(select_query).fetchone() # this is how in version 3 you do things

    print(record)

# test_cursor(cur)


@app.route('/', methods=['GET'])
def inventory():
    query = request.args.get('query') # access the search query
    print(query)
    tagIDs = request.args.getlist('tagIDs') # access the tags
    categoryID =  request.args.get('categoryID') # access the category
    if not (any([query, tagIDs, categoryID])): # Return all results if no conditions
        record = cur.execute('''SELECT propID, prop.name AS propName, description, location.name AS locationName, isBroken
            FROM prop, location
            WHERE prop.locationID = location.locationID;''').fetchall()
    else: # Return wanted things
        
        if not tagIDs:
            tagIDs = [1]
        if not categoryID:
            categoryID = 1
        query = '%' + query + '%'
        record = cur.execute('''
            SELECT propID, prop.name AS propName, isBroken, location.name AS locationName
            FROM prop
            JOIN prop_tag USING (propID)
            JOIN location USING (locationID)
            WHERE tagID = ANY (%(tagIDs)s)
            AND prop.name LIKE %(query)s
            AND categoryID = ANY (%(categoryID)s)
            GROUP BY propID, location.name
            HAVING count(*) = %(tagLen)s
            ;''', {'query': query, 'categoryID':categoryID, 'tagIDs':tagIDs, 'tagLen': len(tagIDs)}).fetchall()
        # https://elliotchance.medium.com/handling-tags-in-a-sql-database-5597b9894049
        # Filter using tags - select those who have all tags in query.
        
        
    # print(record)
    return json.dumps(record)

@app.route('/prop/<int:id>', methods=['GET', 'POST'])
def add_prop(id):
    propID = id
    if request.method == 'GET':
        # Return the prop with the ID
        record = cur.execute('''
            SELECT propID, prop.name AS propName, description, location.name AS locationName, isBroken
            FROM prop, location
            WHERE prop.locationID = location.locationID
            AND prop.propID = (%(propID)s)
            ;''', {'propID': propID}).fetchall()
        return record
    elif request.method == 'POST':
        # Retrieve form data
        request.files['image'] # fly this over to imgur
        request.form['name']
        # Add the record
        id = cur.execute('''INSERT INTO prop (name, description,  categoryID, locationID) 
                         VALUES (%s,%s,%s,%s) 
                         RETURNING propID''')
        return json.dumps(id)
    elif request.method == 'PUT':
        # update the prop
        cur.execute('''UPDATE prop (name, description,  categoryID, locationID) 
                         = (%s,%s,%s,%s) 
                         WHERE propID = %s''', [propID])
        return propID
    elif request.method == 'DELETE':
        cur.execute('''DELETE FROM prop WHERE propID = %(propID)s''', {'propID': propID})
        return "Delete successful"
    
# @app.route('/prop/<int:id>', methods=['GET', 'PUT', 'DELETE'])
# def manipulate_prop():
#     pass