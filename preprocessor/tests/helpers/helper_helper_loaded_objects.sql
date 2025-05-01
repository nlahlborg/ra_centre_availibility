CREATE SCHEMA IF NOT EXISTS helper;

CREATE TABLE helper.helper_loaded_objects (
    object_name VARCHAR
);
INSERT INTO helper.helper_loaded_objects (object_name) VALUES
	 ('raw_centre_raw_20250426T000200Z.json'),
	 ('raw_centre_raw_20250426T000433Z.json'),
	 ('raw_centre_raw_20250426T000722Z.json'),
	 ('raw_centre_raw_20250426T031016Z.json'),
	 ('raw_centre_raw_20250426T031327Z.json'),
	 ('raw_centre_raw_20250426T032417Z.json'),
	 ('raw_centre_raw_20250426T032903Z.json'),
	 ('raw_centre_raw_20250426T034719Z.json'),
	 ('raw_centre_raw_20250426T210454Z.json'),
	 ('raw_centre_raw_20250427T213331Z.json');