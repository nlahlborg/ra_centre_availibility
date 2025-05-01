CREATE SCHEMA IF NOT EXISTS source;

CREATE TABLE "source".reservation_system_events (
	event_id serial4 NOT NULL,
	num_people int4 NOT NULL,
	scraped_datetime timestamptz NULL,
	week_number int4 NULL,
	facility_id int4 NULL,
	timeslot_id int4 NULL,
	inserted_datetime timestamptz NULL,
	CONSTRAINT reservation_system_events_pk PRIMARY KEY (event_id)
);
INSERT INTO "source".reservation_system_events (num_people,scraped_datetime,week_number,facility_id,timeslot_id,inserted_datetime) VALUES
	 (1,'2025-04-26 00:07:02.000',6,1,1,'2025-04-30 13:15:10.031');
