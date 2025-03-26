-- Basic inventory features

CREATE TABLE IF NOT EXISTS category (
        categoryID SERIAL PRIMARY KEY ,
        name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS location (
        locationID SERIAL PRIMARY KEY ,
        name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS prop (
        propID SERIAL PRIMARY KEY,
        name VARCHAR(50) NOT NULL,
        description TEXT,
        categoryID INTEGER REFERENCES category(categoryID),
        isBroken BOOL NOT NULL,
        locationID INTEGER REFERENCES location(locationID),
        photoPath TEXT
);

CREATE TABLE IF NOT EXISTS costume (
        size VARCHAR(50) NOT NULL,
        material VARCHAR(50)
) INHERITS (prop);

CREATE TABLE IF NOT EXISTS tag (
        tagID SERIAL PRIMARY KEY,
        name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS prop_tag (
        tagID INTEGER REFERENCES tag(tagID),
        propID INTEGER REFERENCES prop(propID),
        PRIMARY KEY (tagID, propID)
);


-- User management

CREATE TABLE IF NOT EXISTS appUser (
        userID SERIAL PRIMARY KEY,
        name VARCHAR(50) NOT NULL,
        status VARCHAR(10) NOT NULL,
        emailAddress VARCHAR(255) NOT NULL
);

-- Virtual props list features

CREATE TABLE IF NOT EXISTS star (
        propID INTEGER REFERENCES prop(propID),
        authorID INTEGER REFERENCES appUser(userID),
        timeStarred TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ,
        PRIMARY KEY (propID, authorID)
);



CREATE TABLE IF NOT EXISTS production (
        productionID SERIAL PRIMARY KEY,
        title VARCHAR(50) NOT NULL,
        firstShowDate DATE, --needs a reminder to be updated later if not there
        lastShowDate DATE, -- ditto
        directorID INTEGER REFERENCES appUser(userID),
        producerID INTEGER REFERENCES appUser(userID),
        isArchived BOOL NOT NULL DEFAULT FALSE

);

ALTER TABLE production 
ADD photoPath TEXT;

CREATE TABLE IF NOT EXISTS crew_production (
        crewID INTEGER REFERENCES appUser(userID),
        productionID INTEGER REFERENCES production(productionID),
        role VARCHAR(50) NOT NULL,
        PRIMARY KEY (userID, productionID)
);


CREATE TABLE IF NOT EXISTS propsList (
        propsListID SERIAL PRIMARY KEY,
        title VARCHAR(50) NOT NULL,
        productionID INTEGER NOT NULL REFERENCES production(productionID)
);

CREATE TABLE IF NOT EXISTS propsListItem (
        propsListItemID SERIAL PRIMARY KEY,
        propsListID INTEGER NOT NULL REFERENCES propsList(propsListID),
        name VARCHAR(50) NOT NULL,
        description TEXT,
        sourceStatus VARCHAR(50),
        action VARCHAR(50),
        propID INTEGER NOT NULL REFERENCES prop(propID)

);
ALTER TABLE propsListItem
ALTER COLUMN propID DROP NOT NULL;

CREATE TABLE IF NOT EXISTS costumeListItem (
        size VARCHAR(50), 
        fittingStatus TEXT
) INHERITS (propsListItem);

-- Task management
CREATE TABLE IF NOT EXISTS task (
        taskID SERIAL PRIMARY KEY,
        title VARCHAR(50) NOT NULL,
        description TEXT,
        authorID INTEGER NOT NULL REFERENCES appUser(userID),
        timeCreated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ,
        productionID INTEGER REFERENCES production(productionID),
);

CREATE TABLE IF NOT EXISTS task_crew (
        userID INTEGER REFERENCES appUser(userID),
        taskID INTEGER REFERENCES task(taskID),
        PRIMARY KEY (userID, taskID)
);


