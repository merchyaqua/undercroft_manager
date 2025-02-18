from flask import Flask
from flask import render_template, request, redirect
import psycopg
from dotenv import load_dotenv
import os
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
        conn = psycopg.connect(host=HOST, user=USER, password=PASSWORD, port=PORT, dbname=DBNAME)
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


@app.route('/props', methods=['GET'])
def inventory():
    query = request.args.get('q')
    if query == None:
        record = cur.execute('''SELECT name FROM prop;''').fetchone()
    else:
        record = cur.execute('''SELECT name FROM prop WHERE name LIKE %(query)s;''', {'query': query}).fetchone() # this is how in version 3 you do things
    print(record)
    return render_template('index.html', message=record[0]+'Hey there welcome to the Undercroft')

@app.route('/prop', methods=['GET', 'POST'])
def add_prop():
    if request.method == 'GET':
        return render_template('add_prop.html')
    elif request.method == 'POST':
        request.files['image'] # fly this over to imgur
        request.form['name']
        id = cur.execute('''INSERT INTO prop (name, description, categoryID, locationID) VALUES (%s,%s,%s,%s) RETURNING propID''')
        return redirect('')
    
@app.route('/prop/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def manipulate_prop():
    pass