CREATE SCHEMA IF NOT EXISTS helper;

CREATE TABLE "helper".helper_loaded_objects (
	object_name varchar NOT NULL
);
INSERT INTO "helper".helper_loaded_objects (object_name) VALUES
	 ('raw_centre_raw_20250426T000200Z.json'),
	 ('raw_centre_raw_20250426T000433Z.json')