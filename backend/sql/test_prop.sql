-- INSERT INTO location (name) VALUES ('Undercroft') RETURNING locationID;
-- INSERT INTO category (name) VALUES ('Weapons') RETURNING categoryID;
-- INSERT INTO tag (name) VALUES ('Medieval');


-- INSERT INTO prop (name, description, categoryID, isBroken, locationID, photoPath)
-- VALUES (
--     'Sword',
--     'Great for breaking fingers',
--     (SELECT categoryID FROM category WHERE name = 'Weapons'),
--     FALSE,
--     (SELECT locationID FROM location WHERE name = 'Undercroft'),
--     'https://images.unsplash.com/photo-1558642452-9d2a7deb7f62?w=248&fit=crop&auto=format'
-- );

-- INSERT INTO prop_tag (
--     propID, tagID
-- ) VALUES (
--     (SELECT propID FROM prop WHERE name = 'Sword'), 
--     (SELECT tagID FROM tag WHERE name = 'Medieval')
--     );

-- very good - add to design
-- SELECT propID 
-- FROM prop 
-- JOIN prop_tag USING (propID)
-- WHERE tagID IN (1, 2) 
-- AND name LIKE 'Sword'
-- AND categoryID = 1
-- GROUP BY propID
-- HAVING count(*) = 2
-- ;

-- SELECT propID, prop.name AS propName, description, location.name AS locationName, isBroken
-- FROM prop, location
-- WHERE prop.locationID = location.locationID
-- AND prop.propID = 2
-- ;


-- DELETE FROM prop WHERE propID = 2;


-- INSERT INTO location (name) VALUES ('Undercroft') RETURNING locationID;


-- DROP TABLE prop;
-- DROP TABLE location;
-- DROP TABLE category;

-- Ensure the productionID exists in the production table
INSERT INTO production (productionID, name) VALUES (2, 'Production Name');

INSERT INTO propsList (title, productionID) VALUES ('Props', 2);