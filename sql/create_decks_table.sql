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

CREATE TABLE decks (
	deck_id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
	event_id INT UNSIGNED NOT NULL,
	deck_title VARCHAR (255) NOT NULL,
	deck_format VARCHAR (255) NOT NULL,
	placement VARCHAR (16) NOT NULL,
	deck_author VARCHAR (255) NOT NULL,
	FOREIGN KEY (event_id) REFERENCES events (id) ON DELETE NO ACTION ON UPDATE NO ACTION
);
