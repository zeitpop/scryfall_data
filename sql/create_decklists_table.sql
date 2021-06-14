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

CREATE TABLE decklists (
	id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	deck_id INT UNSIGNED NOT NULL,
	card_id INT NOT NULL,
	card_name VARCHAR(255) NOT NULL,
	count_maindeck TINYINT UNSIGNED NOT NULL,
	count_sideboard TINYINT UNSIGNED NOT NULL,
	FOREIGN KEY (deck_id) REFERENCES decks (deck_id) ON DELETE CASCADE ON UPDATE NO ACTION,
	FOREIGN KEY (card_id) REFERENCES cards (internal_card_id)

);
