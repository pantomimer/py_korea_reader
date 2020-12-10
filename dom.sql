CREATE TABLE "sentences" (
	"id"	INTEGER,
	"sentence"	TEXT,
	"is_read"	INTEGER DEFAULT 0,
	PRIMARY KEY("id" AUTOINCREMENT)
)
CREATE TABLE "words" (
	"id"	INTEGER,
	"word"	TEXT UNIQUE,
	"mean"	TEXT,
	"read_num"	INTEGER,
	"check_num"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
)

CREATE TABLE sqlite_sequence(name,seq)
