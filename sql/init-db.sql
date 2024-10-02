CREATE TABLE CIRCUIT(
	PK_CIRCUIT INT unsigned AUTO_INCREMENT PRIMARY KEY,
	GUID varchar(40) NOT NULL,
	NAME varchar(255) NOT NULL,
	COUNTRY varchar(50) NOT NULL,
	FLAG_PATH varchar(255) NULL,
	PLACEHOLDER_PATH varchar(255) NULL,
	DOI DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	DOU DATETIME NULL
);

CREATE TABLE EVENT(
	PK_EVENT INT unsigned AUTO_INCREMENT PRIMARY KEY,
	FK_CIRCUIT INT unsigned NOT NULL,
	GUID varchar(40) NOT NULL,
	NAME varchar(255) NOT NULL,
	KIND varchar(255) NOT NULL,
	SEASON varchar(4) NOT NULL,
	START_DATE DATE NOT NULL,
	END_DATE DATE NOT NULL,
	DOI DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	DOU DATETIME NULL,
	FOREIGN KEY(FK_CIRCUIT) REFERENCES CIRCUIT(PK_CIRCUIT)
);

CREATE TABLE BROADCASTER(
	PK_BROADCASTER INT unsigned AUTO_INCREMENT PRIMARY KEY,
	NAME VARCHAR(255) NOT NULL,
	DOI DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	DOU DATETIME NULL
);
INSERT INTO BROADCASTER(NAME)VALUES("MOTOGP"),("TV8");

CREATE TABLE CATEGORY(
	PK_CATEGORY INT unsigned AUTO_INCREMENT PRIMARY KEY,
	GUID VARCHAR(40) NOT NULL,
	NAME VARCHAR(255) NOT NULL,
	ACRONYM VARCHAR(10) NOT NULL,
	DOI DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	DOU DATETIME NULL
);
INSERT INTO CATEGORY
	(GUID, NAME, ACRONYM) 
VALUES
	("93888447-8746-4161-882c-e08a1d48447e","MotoGP", "MGP"),
	("df13030a-4d5d-47b0-8b07-99943e5ce786", "MotoE", "MTE"),
	("bc2b0143-1bfb-4ad0-9501-da2e474e3ea7", "Moto2", "MT2"),
	("7b0adf61-0a93-4e3d-a7ef-1fee93c2591f", "Moto3", "MT3");


CREATE TABLE BROADCAST(
	PK_BROADCAST INT unsigned AUTO_INCREMENT PRIMARY KEY,
	FK_EVENT INT unsigned NOT NULL,
	FK_BROADCASTER INT unsigned NOT NULL,
	FK_CATEGORY INT unsigned NULL,
	GUID VARCHAR(40) NULL,
	NAME VARCHAR(255) NOT NULL,
	IS_LIVE TINYINT(1) NOT NULL,
	START_DATE DATE NOT NULL,
	END_DATE DATE NULL,
	DOI DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	DOU DATETIME NULL,
	FOREIGN KEY(FK_EVENT) REFERENCES EVENT(PK_EVENT),
	FOREIGN KEY(FK_BROADCASTER) REFERENCES BROADCASTER(PK_BROADCASTER),
	FOREIGN KEY(FK_CATEGORY) REFERENCES CATEGORY(PK_CATEGORY)
);