CREATE TABLE KIND (
	PK_KIND INT UNSIGNED auto_increment NOT NULL,
	NAME varchar(100) NOT NULL,
	DOI DATETIME DEFAULT CURRENT_TIMESTAMP  NOT NULL,
	CONSTRAINT KIND_PK PRIMARY KEY (PK_KIND)
);
INSERT INTO KIND
	(PK_KIND, NAME)
VALUES
	(1, "Qualifying"),
	(2, "Race");

ALTER TABLE 
	BROADCAST
ADD COLUMN 
	`FK_KIND` INT unsigned NULL AFTER `FK_CATEGORY`;

ALTER TABLE 
	BROADCAST 
ADD CONSTRAINT 
	FOREIGN KEY (FK_KIND) REFERENCES KIND(PK_KIND);