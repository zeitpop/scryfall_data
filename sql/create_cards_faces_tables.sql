/*
--------------------------------------------------------------------
Scryfall API Database Schema, Not affiliated with Scryfall
--------------------------------------------------------------------
Alex Koure 
--------------------------------------------------------------------
*/
-- create schemas
-- CREATE SCHEMA scryfall;

-- Select the schema
USE scryfall;

-- create tables
CREATE TABLE cards (
	internal_card_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	scryfall_card_id VARCHAR (255),
	arena_id INT,
	lang VARCHAR (255) NOT NULL,
	object VARCHAR (255) NOT NULL,
	oracle_id VARCHAR (255) NOT NULL,
	scryfall_uri VARCHAR (255) NOT NULL,
	uri VARCHAR (255) NOT NULL,
	card_face_id INT,
	cmc DECIMAL (19,4) NOT NULL,
	color_identity VARCHAR (255) NOT NULL,
	color_indicator VARCHAR (255),
	colors VARCHAR (255),
	layout VARCHAR (255) NOT NULL,
	loyalty VARCHAR (255),
	mana_cost VARCHAR (255),
	name VARCHAR (255) NOT NULL,
	oracle_text VARCHAR (1023),
	power VARCHAR (255),
	produced_mana VARCHAR (255),
	toughness VARCHAR (255),
	type_line VARCHAR (255) NOT NULL,
	flavor_text VARCHAR (511), 
	rarity VARCHAR (16),
	release_at DATETIME,
	reprint BOOLEAN,
	set_name VARCHAR (255),
	set_type VARCHAR (255),
	set_code VARCHAR (8)
	
);

CREATE TABLE card_faces (
	card_face_id INT PRIMARY KEY,
	parent_card_id INT,
	color_indicator VARCHAR (255),
	colors VARCHAR (255), 
	flavor_text VARCHAR (255),
	loyalty VARCHAR (255),
	mana_cost VARCHAR (255) NOT NULL,
	name VARCHAR (255) NOT NULL,
	object VARCHAR(255) NOT NULL,
	oracle_text VARCHAR(1023),
	power VARCHAR (255),
	toughness VARCHAR (255),
	type_line VARCHAR (255) NOT NULL,
	FOREIGN KEY (parent_card_id) REFERENCES cards(internal_card_id)
);
