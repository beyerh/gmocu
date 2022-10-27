DROP TABLE IF EXISTS Plasmids;
DROP TABLE IF EXISTS SelectionValues;
DROP TABLE IF EXISTS Attachments;
DROP TABLE IF EXISTS Cassettes;
DROP TABLE IF EXISTS GMOs;
DROP TABLE IF EXISTS OrganismSelection;
DROP TABLE IF EXISTS OrganismFavourites;
DROP TABLE IF EXISTS Features;
DROP TABLE IF EXISTS Organisms;
DROP TABLE IF EXISTS Settings;

CREATE TABLE Plasmids(
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"name" TEXT DEFAULT "pXX000",
	"alias" TEXT,
	"status" INTEGER DEFAULT 4,
	"gb" TEXT,
	"purpose" TEXT,
	"summary" TEXT,
	"genebank" TEXT,
	"gb_name" TEXT,
	"FKattachment" INTEGER,
	"clone" TEXT,
	"backbone_vector" TEXT,
	"marker" TEXT,
	"organism_selector" INTEGER,
	"target_RG" INTEGER DEFAULT 1,
	"generated" INTEGER DEFAULT (date('now')),
	"destroyed" INTEGER,
	"date" INTEGER DEFAULT (date('now')),
	FOREIGN KEY(status) REFERENCES SelectionValues(id)
	FOREIGN KEY(organism_selector) REFERENCES OrganismSelection(organism_name)
);

CREATE TABLE SelectionValues(
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "value" TEXT DEFAULT "Planned"
);

CREATE TABLE Attachments(
	"file" BLOB,
	"Filename" TEXT,
    "attach_id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"plasmid_id" INTEGER,
	FOREIGN KEY(plasmid_id) REFERENCES Plasmids(id) ON UPDATE CASCADE
);

CREATE TABLE Cassettes(
	"cassette_id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"content" TEXT DEFAULT "Empty",
	"plasmid_id" INTEGER,
	FOREIGN KEY(plasmid_id) REFERENCES Plasmids(id) ON UPDATE CASCADE
);

CREATE TABLE GMOs(
	"organism_id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"GMO_summary" TEXT,
	"organism_name" TEXT,
	"approval" TEXT,
	"plasmid_id" INTEGER,
	"target_RG" INTEGER,
	"date_generated" INTEGER DEFAULT (date('now')),
	"date_destroyed" INTEGER,
	"entry_date" INTEGER,
	FOREIGN KEY(plasmid_id) REFERENCES Plasmids(id) ON UPDATE CASCADE
);

CREATE TABLE OrganismSelection(
	"orga_sel_id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"organism_name" TEXT
);

CREATE TABLE OrganismFavourites(
	"orga_fav_id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"organism_fav_name" TEXT
);

CREATE TABLE Features(
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "annotation" TEXT,
	"alias" TEXT,
	"risk" TEXT DEFAULT 'None',
	"organism" TEXT
);

CREATE TABLE Organisms(
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "full_name" TEXT,
	"short_name" TEXT, 
	"RG" TEXT
);

CREATE TABLE Settings(
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" TEXT,
	"initials" TEXT,
	"email" TEXT,
	"institution" TEXT,
	"ice" INTEGER,
	"gdrive_glossary" TEXT,
	"duplicate_gmos" INTEGER DEFAULT 0,
	"upload_completed" INTEGER DEFAULT 0,
	"upload_abi" INTEGER DEFAULT 0,
	"scale" INTEGER DEFAULT 1,
	"font_size" INTEGER DEFAULT 13,
	"style" TEXT DEFAULT 'Reddit',
	FOREIGN KEY(ice) REFERENCES IceCredentials(id)
);

CREATE TABLE IceCredentials(
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "alias" TEXT,
	"ice_instance" TEXT,
	"ice_token_client" TEXT,
	"ice_token" TEXT
);

INSERT INTO SelectionValues VALUES (1,"Complete");
INSERT INTO SelectionValues VALUES (2,"In Progress");
INSERT INTO SelectionValues VALUES (3,"Abandoned");
INSERT INTO SelectionValues VALUES (4,"Planned");

INSERT INTO Settings VALUES (1, 'Name','__','xxx@xxx.com', 'Az.: xxx / Anlage Nr.: xxx', 1, 'ID from link', 0, 0, 0, 1, 13, 'Reddit');
INSERT INTO IceCredentials VALUES (1, 'ICE-lab.local','https://public-registry.jbei.org/','X-ICE-API-Token-Client', 'X-ICE-API-Token');