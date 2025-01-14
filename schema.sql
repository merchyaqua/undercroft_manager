
-- Enable foreign key constraints
PRAGMA foreign_keys = ON;


CREATE TABLE IF NOT EXISTS category (
        categoryID INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(50) NOT NULL,
);
CREATE TABLE IF NOT EXISTS location (
        locationID INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(50) NOT NULL,
);

CREATE TABLE IF NOT EXISTS prop (
        propID INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(50) NOT NULL,
        description TEXT,
        categoryID INTEGER,
        isBroken INTEGER NOT NULL,
        locationID INTEGER,
        photoPath TEXT,
        FOREIGN KEY (categoryID) REFERENCES category(categoryID),
        FOREIGN KEY (locationID) REFERENCES location(locationID)
    );