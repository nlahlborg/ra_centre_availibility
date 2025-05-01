CREATE SCHEMA IF NOT EXISTS source;

CREATE TABLE "source".timeslots (
	timeslot_id serial4 NOT NULL,
	start_time timetz NOT NULL,
	end_time timetz NULL,
	day_of_week varchar NOT NULL,
	release_interval_days int4 NOT NULL,
	CONSTRAINT timeslots_pk PRIMARY KEY (timeslot_id)
);
INSERT INTO "source".timeslots (start_time,end_time,day_of_week,release_interval_days) VALUES
	 ('12:00:00','13:00:00','Friday',7)

