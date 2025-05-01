CREATE SCHEMA IF NOT EXISTS source;

CREATE TABLE "source".facilities (
	facility_id serial4 NOT NULL,
	facility_name varchar NOT NULL,
	facility_type varchar NOT NULL,
	CONSTRAINT facilities_pk PRIMARY KEY (facility_id)
);
INSERT INTO "source".facilities (facility_name,facility_type) VALUES
	 ('Badminton Court 1','badminton_court')
