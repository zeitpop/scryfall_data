/*
--------------------------------------------------------------------
Create Decklist Table
--------------------------------------------------------------------
Alex Koure 
--------------------------------------------------------------------
*/

-- Select the schema
USE scryfall;

-- create tables

CREATE TABLE events (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
	event_name VARCHAR(255) NOT NULL,
        event_date DATE NOT NULL,
        event_format VARCHAR (255) NOT NULL,
	event_link VARCHAR (511) NOT NULL
);
