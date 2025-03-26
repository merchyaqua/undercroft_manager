from flask import Flask, jsonify
from flask import request, redirect
from flask_cors import CORS
from connect_db import connect
app = Flask(__name__)
# Ensure the frontend running on a different port is allowed to request data
CORS(app)

conn = connect()
cur = conn.cursor()


@app.route('/prop', methods=['GET', 'POST'])
def inventory():
    if request.method =="GET":
        query = request.args.get('query') # access the search query
        tagIDs = request.args.getlist('tagIDs') # access the tags
        categoryID =  request.args.get('categoryID') # access the category
        print(query, categoryID)
        # Return all results if no parameters are provided
        # Initially, I used this code for optional query parameters. However, this was inefficient since I was running a query for every single prop.
        # Return wanted things
        newquery = query
        sqlQuery = """
            SELECT prop.propID, prop.name AS propName, isBroken, location.name AS locationName, prop.photoPath,
                CASE 
                    WHEN production.productionID IS NULL 
                    THEN 1 
                    ELSE 0
                END AS available
            FROM prop

            JOIN location USING(locationID)
            LEFT JOIN propsListItem ON propsListItem.propID = prop.propID
            LEFT JOIN propsList ON propsList.propsListID = propsListItem.propsListID
            LEFT JOIN production ON 
                propsList.productionID = production.productionID
                AND production.lastShowDate > NOW() -- Only include ongoing productions

            WHERE
                COALESCE(%(query)s) IS NULL OR UPPER(prop.name) LIKE UPPER((%(query)s::text))
                AND COALESCE(%(categoryID)s) IS NULL OR categoryID = %(categoryID)s::int

            GROUP BY (prop.propID, location.name, production.productionID);
        """
    #     sqlQuery = f'''
    #         SELECT propID, prop.name AS propName, isBroken, location.name AS locationName, photoPath
    #         FROM prop
    #         {"JOIN prop_tag USING (propID)"  if tagIDs else ''}
    #         JOIN location USING (locationID)
    #         WHERE 
    #         NOT propID = -1 
    #         {"AND tagID = ANY (%(tagIDs)s)" if tagIDs else ''}
    #         {"AND UPPER(prop.name) LIKE UPPER(%(query)s)" if query else ''}
    #         {"AND categoryID = %(categoryID)s" if categoryID else ''}
    #         GROUP BY propID, location.name
    #         {"HAVING count(*) = %(tagLen)s" if tagIDs else ''}
            
    #         ;'''
    #     print(sqlQuery)
        records = cur.execute(sqlQuery, {'query': newquery if newquery else None, 
                                            'categoryID':int(categoryID) if categoryID else None, 
                                            'tagIDs':tagIDs, 'tagLen': len(tagIDs)}).fetchall()
    #     # 
    #     # Filter using tags - select those who have all tags in query.
        
    #     # clever find status by:
    #     # Checking that it is not broken
    # newRecords = []
    # for record in records:
    #         available = cur.execute('''SELECT COUNT(propsListItemID)=0 AS available
    #                         FROM propsListItem, propsList, production, prop
    #                         WHERE propsListItem.propID = %(propID)s -- Has been linked to an item
    #                         AND production.lastShowDate > NOW() -- The show has not concluded
    #                         AND propsListItem.propsListID = propsList.propsListID -- Linking by foreign keys
    #                         AND propsList.productionID = production.productionID;''', {"propID": record['propid']}).fetchone()
    #         record['available'] = available['available']
    #         newRecords.append(record)
                
        return jsonify(records)
    elif request.method == 'POST':
        # Retrieve form data in a dict format to pass to psycopg
        data = dict(request.get_json())
        # Add the record
        data['isBroken'] = data['isBroken'] == "on"
        res = cur.execute('''INSERT INTO prop (name, description, isBroken, categoryID, locationID, photoPath) 
                         VALUES (%(name)s,%(description)s, %(isBroken)s, %(categoryID)s,%(locationID)s, %(photoPath)s) 
                         RETURNING propID''', data).fetchone()
        return jsonify(res)

@app.route('/prop/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def prop_detail(id):
    propID = id
    if request.method == 'GET':
        # Return the prop with the ID
        record = cur.execute('''
            SELECT propID, prop.name AS propName, description, location.name AS locationName, isBroken, photoPath
            FROM prop, location
            WHERE prop.locationID = location.locationID
            AND prop.propID = (%(propID)s)
            ;''', {'propID': propID}).fetchone()
        # see if any upcoming productions involve this prop
        available = cur.execute('''SELECT COUNT(propsListItemID)=0 AS available
                                FROM propsListItem, propsList, production, prop
                                WHERE propsListItem.propID = %(propID)s -- Has been linked to an item
                                AND production.lastShowDate > NOW() -- The show has not concluded
                                AND propsListItem.propsListID = propsList.propsListID -- Linking by foreign keys
                                AND propsList.productionID = production.productionID;''', {"propID": propID}).fetchone()
        if not record:
            return redirect("/not-found")
        record["available"] = int(available["available"])
        print((record))
        return jsonify(record)
    elif request.method == 'PUT':
        # Update the prop with given data
        data = dict(request.get_json())
        cur.execute('''UPDATE prop 
                        SET (name, description,  categoryID, locationID) 
                         = (%(name)s,%(description)s,%(categoryID)s,%(locationID)s) 
                         WHERE propID = %s''', data)
        return propID
    elif request.method == 'DELETE':
        cur.execute('''DELETE FROM prop WHERE propID = %(propID)s''', {'propID': propID})
        return jsonify("Delete successful")

@app.route('/category', methods=['GET', 'POST'])
def category():
    if request.method == 'GET':
        record = cur.execute('''
            SELECT name, categoryID FROM category;''').fetchall()
        return jsonify(record)
    elif request.method == 'POST':
        categoryID = cur.execute('''
            INSERT INTO category (name) VALUES (%s) RETURNING categoryID;''', [request.get_json()['name']]).fetchone()
        print(categoryID)
        return jsonify(categoryID['categoryid'])

@app.route('/location', methods=['GET', 'POST'])
def location():
    if request.method == 'GET':
        record = cur.execute('''
            SELECT name, locationID FROM location;''').fetchall()
        return jsonify(record)
    elif request.method == 'POST':
        locationID = cur.execute('''
            INSERT INTO location (name) VALUES (%s) RETURNING locationID;''', [request.get_json()['name']]).fetchone()
        print(locationID)
        return jsonify(locationID['locationid'])
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
        
        data = dict(request.get_json())
        productionID = cur.execute('''
            INSERT INTO production (title, firstShowDate, lastShowDate, photoPath) 
            VALUES (%(title)s,%(firstShowDate)s,%(lastShowDate)s, %(photoPath)s)
            RETURNING productionID;
        ''', data).fetchone() # check if the dates go in fine - and is it best to store date not big int for js ms
        return productionID

@app.route('/production/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def production_detail(id):
    if request.method == 'GET':
        # Return all details about a production
        record = cur.execute('''
            SELECT * FROM production WHERE productionID = %s;''', [id]).fetchone()
        return jsonify(record)
    elif request.method == 'PUT': 
        # Update production details.
        data = dict(request.get_json())
        cur.execute('''UPDATE production (name, firstShowDate, lastShowDate, photoPath) 
            SET (%(name)s,%(firstShowDate)s,%(lastShowDate)s,%(photoPath)s)
            WHERE productionID = %(productionID)s''', data.update({'productionID': id})) # Concatenate the form MultiDict with productionID as a new key value pair.
            
        return id
    elif request.method == 'DELETE':
        cur.execute('''DELETE FROM production WHERE productionID = %(productionID)s''', {'productionID': id})
        return jsonify("Delete successful")

@app.route('/production/<int:productionID>/props-list', methods=['GET', 'POST'])
def props_list(productionID):
    # Return the ID and title props lists for a production
    if request.method == 'GET':
        record = cur.execute('''
            SELECT propsListID, propsList.title AS propsListTitle, production.title AS productionTitle
            FROM propsList, production 
            WHERE propsList.productionID = %s
            AND propsList.productionID = production.productionID;''', [productionID]).fetchall()
        print(record)
        return jsonify(record)
    elif request.method == 'POST':
    # Create a new props list for production, returning propsListID for redirecting.
        propsListID = cur.execute('''
            INSERT INTO propsList (productionID, title) 
            VALUES (%(productionID)s,%(title)s)
            RETURNING propsListID;
        ''', {'productionID': productionID, 'title':request.get_json()['title']}).fetchone() # not sure if i need to fetch for the id to be returned
        return jsonify(propsListID)
    
@app.route('/props-list/<int:propsListID>', methods=['GET','POST','PUT', 'DELETE'])
def props_list_details(propsListID):
    # Return all the props list items with details / the name of the production for a props list given the propsListID
    if request.method == 'GET':
        titleInfo = cur.execute("""SELECT production.title AS productionTitle, propsList.title AS propsListTitle
                                       FROM production, propsList
                                       WHERE propsListID = %(propsListID)s
                                       AND production.productionID = propsList.productionID;""", 
                                       {'propsListID': propsListID}).fetchone()
        propsListItems = cur.execute("SELECT * FROM propsListItem WHERE propsListID = %(propsListID)s;", {'propsListID': propsListID}).fetchall()
        return jsonify({'productionTitle': titleInfo['productiontitle'],
                        'propsListTitle': titleInfo['propslisttitle'],
                         'propsListItems': propsListItems})
    elif request.method == "POST":
        # Create a new entry to this props list, returning propsListItemID for client to reference for further operations
        data = dict(request.get_json())
        data['propsListID'] = propsListID
        propsListItemID = cur.execute('''
            INSERT INTO propsListItem (propsListID, name, description, sourceStatus, action) 
            VALUES (%(propsListID)s,%(name)s, %(description)s, %(sourceStatus)s, %(action)s)
            RETURNING propsListItemID;
        ''', data).fetchone() 
        return jsonify(propsListItemID)
    elif request.method == "DELETE":
        cur.execute("DELETE FROM propsList WHERE propsListID = %s", [propsListID])
        return jsonify("Delete successful for propsListID " + propsListID)


@app.route('/props-list-item/<int:propsListItemID>', methods=['GET', 'PUT', 'DELETE'])
def props_list_item(propsListItemID):
    # Returns the fields for particular a record of a props list item given propsListItemID, allowing updates
    if request.method == 'GET':
        propsListItem = cur.execute("SELECT * FROM propsListItems WHERE propsListItemID = %(propsListItemID)s;", {'propsListItemID': propsListItemID}).fetchone()
        return jsonify(propsListItem)
    elif request.method == 'PUT':
        data = dict(request.get_json()) # maybe make consistent across all post requests
        print(data)
        data["propsListItemID"] = propsListItemID
        cur.execute('''UPDATE propsListItem 
                    SET (name, description, sourcestatus, action) = 
                    (%(name)s, %(description)s, %(sourceStatus)s, %(action)s) 
                    WHERE propsListItemID = %(propsListItemID)s;''', data)
        return jsonify("Update successful")
    elif request.method == "DELETE":
        cur.execute("DELETE FROM propsListItem WHERE propsListItemID = %(propsListItemID)s;", {'propsListItemID': propsListItemID})
        return jsonify("Delete successful")

@app.route('/props-list-item/<int:propsListItemID>/link', methods=['PUT'])
def props_list_item_link(propsListItemID):
    # Link a prop
    if request.method == 'PUT':
        data = dict(request.get_json())
        data["propsListItemID"] = propsListItemID
        print(data)
        cur.execute('''UPDATE propsListItem 
                    SET (propID) = ROW(%(propID)s)
                    WHERE propsListItemID = %(propsListItemID)s;''', data)
        return jsonify("Prop link successful")
          




# Ignore:
# Wrestling with conventions here - should i haver a propslistitem/ or proplslistitem/link/propid ??? argh