INSERT INTO location (name) VALUES ('Undercroft') RETURNING locationID;
INSERT INTO category (name) VALUES ('Weapons') RETURNING categoryID;

INSERT INTO prop (name, description, categoryID, isBroken, locationID, photoPath)
VALUES (
    'Sword',
    'Great for breaking fingers',
    (SELECT categoryID FROM category WHERE name = 'Weapons'),
    FALSE,
    (SELECT locationID FROM location WHERE name = 'Undercroft'),
    'test photopath'
);

INSERT INTO tag (name) VALUES ('Medieval');


-- DELETE FROM prop WHERE propID = 2;


-- INSERT INTO location (name) VALUES ('Undercroft') RETURNING locationID;


-- DROP TABLE prop;
-- DROP TABLE location;
-- DROP TABLE category;