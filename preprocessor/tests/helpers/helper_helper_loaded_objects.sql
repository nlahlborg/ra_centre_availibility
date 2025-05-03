CREATE SCHEMA IF NOT EXISTS helper;

CREATE TABLE "helper".helper_loaded_objects (
	object_name varchar NOT NULL,
	scraped_datetime timestamptz NULL
);
INSERT INTO "helper".helper_loaded_objects (object_name, scraped_datetime) VALUES
	 ('raw_centre_raw_20250426T000200Z.json','2025-04-26 00:02:00.000'),
	 ('raw_centre_raw_20250426T000433Z.json','2025-04-26 00:04:33.000')