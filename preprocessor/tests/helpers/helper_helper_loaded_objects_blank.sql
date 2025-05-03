CREATE SCHEMA IF NOT EXISTS helper;

CREATE TABLE "helper".helper_loaded_objects_blank (
	object_name varchar NOT NULL,
	scraped_datetime timestamptz NULL
);