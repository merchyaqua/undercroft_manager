from flask import Flask, jsonify
from flask import render_template, request, redirect
from flask_cors import CORS
from connect_db import connect
app = Flask(__name__)
CORS(app)

conn = connect()
cur = conn.cursor()


@app.route('/prop', methods=['GET', 'POST'])
def inventory():
    if request.method =="GET":
        query = request.args.get('query') # access the search query
        tagIDs = request.args.getlist('tagIDs') # access the tags
        categoryID =  request.args.get('categoryID') # access the category
        if not (any([(not query == ''), tagIDs, categoryID])): # Return all results if no conditions
            record = cur.execute('''SELECT propID, prop.name AS propName, description, location.name AS locationName, isBroken, photoPath
                FROM prop, location
                WHERE prop.locationID = location.locationID;''').fetchall()
        else: # Return wanted things
            
            if not tagIDs:
                tagIDs = [1]
            if not categoryID:
                categoryID = 1
            query = '%' + query + '%'
            record = cur.execute('''
                SELECT propID, prop.name AS propName, isBroken, location.name AS locationName, photoPath
                FROM prop
                JOIN prop_tag USING (propID)
                JOIN location USING (locationID)
                WHERE tagID = ANY (%(tagIDs)s)
                AND UPPER(prop.name) LIKE UPPER(%(query)s)
                AND categoryID = (%(categoryID)s)
                GROUP BY propID, location.name
                HAVING count(*) = %(tagLen)s

                ;''', {'query': query, 'categoryID':categoryID, 'tagIDs':tagIDs, 'tagLen': len(tagIDs)}).fetchall()
            # https://elliotchance.medium.com/handling-tags-in-a-sql-database-5597b9894049
            # Filter using tags - select those who have all tags in query.
            
            # clever find status by:
            # Checking that it is not broken
        # print(record)
        return jsonify(record)
    elif request.method == 'POST':
        # Retrieve form data
        formData = request.get_json()
        data = dict(formData)
        # request.files['image'] # fly this over to imgur
        # request.form['name']
        # Add the record
        data['isBroken'] = data['isBroken'] == "on"
        id = cur.execute('''INSERT INTO prop (name, description, isBroken, categoryID, locationID) 
                         VALUES (%(name)s,%(description)s, %(isBroken)s, %(categoryID)s,%(locationID)s) 
                         RETURNING propID''', data)
        # Autocommit is turned on.
        id = 2
        return jsonify({"propID": id})

@app.route('/prop/<int:id>', methods=['GET', 'PUT'])
def prop_detail(id):
    propID = id
    if request.method == 'GET':
        # Return the prop with the ID
        record = cur.execute('''
            SELECT propID, prop.name AS propName, description, location.name AS locationName, isBroken, photoPath
            FROM prop, location
            WHERE prop.locationID = location.locationID
            AND prop.propID = (%(propID)s)
            ;''', {'propID': propID}).fetchall()
        if not record:
            
            return redirect("/not-found")
        return jsonify(record[0])
    
    elif request.method == 'PUT':
        # Update the prop with given data
        cur.execute('''UPDATE prop 
                        SET (name, description,  categoryID, locationID) 
                         = (%s,%s,%s,%s) 
                         WHERE propID = %s''', [propID])
        return propID
    elif request.method == 'DELETE':
        cur.execute('''DELETE FROM prop WHERE propID = %(propID)s''', {'propID': propID})
        return "Delete successful"
    
# @app.route('/prop/<int:id>', methods=['GET', 'PUT', 'DELETE'])
# def manipulate_prop():
#     pass

# --------------------------------------

@app.route('/category', methods=['GET', 'POST'])
def category():
    if request.method == 'GET':
        record = cur.execute('''
            SELECT name, categoryID FROM category;''').fetchall()
        return jsonify(record)
    elif request.method == 'POST':
        cur.execute('''
            SELECT name, categoryID FROM category;''').fetchall()
        # Then it's the client's responsibility to reload the categories

@app.route('/location', methods=['GET', 'POST'])
def location():
    if request.method == 'GET':
        record = cur.execute('''
            SELECT name, locationID FROM location;''').fetchall()
        return jsonify(record)
    elif request.method == 'POST':
        cur.execute('''
            SELECT name, categoryID FROM category;''').fetchall()
        # Then it's the client's responsibility to reload the categories
    
# --------------------------------------

@app.route('/production', methods=['GET', 'POST'])
def production():
    if request.method == 'GET':
        # Return basic info about all productions
        record = cur.execute('''
            SELECT title, productionID, firstShowDate, lastShowDate, photoPath FROM production;''').fetchall()
        return jsonify(record)
    elif request.method == 'POST':
        # Adding a new production
        formData = request.get_json()
        data = dict(formData)
        productionID = cur.execute('''
            INSERT INTO production (title, firstShowDate, lastShowDate, directorID, producerID, photoPath) 
            VALUES (%(title)s,%(firstShowDate)s,%(lastShowDate)s,%(directorID)s,%(producerID)s,%(photoPath)s)
            RETURNING productionID;
        ''', data).fetchone() # check if the dates go in fine - and is it best to store date not big int for js ms
        return productionID

@app.route('/production/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def production_detail(id):
    if request.method == 'GET':
        # Return all details about a production
        record = cur.execute('''
            SELECT * FROM production WHERE productionID = %s;''', id).fetchall()
        return jsonify(record)
    elif request.method == 'PUT': # TODO change the queries to match
        # Update production details. So annoying to have to write out all the field names though. Is it common practice to have a form like this and have it update the whole thing?
        cur.execute('''UPDATE production (name, firstShowDate, lastShowDate, directorID, producerID, photoPath) 
            SET (%(name)s,%(firstShowDate)s,%(lastShowDate)s,%(directorID)s,%(producerID)s,%(photoPath)s)
            WHERE productionID = %(productionID)s''', request.form + {'productionID': id}) # Concatenate the form MultiDict with productionID as a new key value pair.
            
        return id
    elif request.method == 'DELETE':
        cur.execute('''DELETE FROM production WHERE productionID = %(productionID)s''', {'productionID': id})
        return "Delete successful"

@app.route('/production/<int:productionID>/props-list/', methods=['GET', 'POST'])
def props_list(productionID):
    # Return the ID and title props lists for a production
    if request.method == 'GET':
        record = cur.execute('''
            SELECT (propsListID, propsList.title AS propsListTitle, production.title AS productionListTitle) 
            FROM propsList, production 
            WHERE productionID = %s;''', [productionID]).fetchall()
        return jsonify(record)
    elif request.method == 'POST':
    # Create a new props list for production, returning propsListID for redirecting.
        propsListID = cur.execute('''
            INSERT INTO propsList (productionID, title) 
            VALUES (%(productionID)s,%(title)s)
            RETURNING propsListID;
        ''', {'productionID': productionID, 'title': request.form.get('title')}).fetchone() # not sure if i need to fetch for the id to be returned
        return propsListID
    
@app.route('/props-list/<int:propsListID>', methods=['GET', 'PUT', 'DELETE'])
def props_list_details(propsListID):
    # Return all the props list items for a props list given the propsListID
    if request.method == 'GET':
        propsListItems = cur.execute("SELECT * FROM propsListItem WHERE propsListID = %(propsListID)s;", {'propsListID': propsListID}).fetchall()
        return jsonify(propsListItems)

@app.route('/props-list-item/<int:propsListItemID>', methods=['GET', 'PUT'])
def props_list_item(propsListItemID):
    # Returns the fields for particular a record of a props list item given propsListItemID, allowing updates
    if request.method == 'GET':
        propsListItem = cur.execute("SELECT * FROM propsListItems WHERE propsListItemID = %(propsListItemID)s;", {'propsListItemID': propsListItemID}).fetchone()
        return jsonify(propsListItem)
    elif request.method == 'PUT':
        cur.execute("UPDATE propsListItem SET (fields) = (data) WHERE propsListItemID = %(propsListItemID)s;", {'propsListItemID': propsListItemID}).fetchone()




# Ignore:
# Wrestling with conventions here - should i haver a propslistitem/ or proplslistitem/link/propid ??? argh