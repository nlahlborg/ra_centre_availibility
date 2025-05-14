CREATE SCHEMA IF NOT EXISTS source;

CREATE OR REPLACE VIEW "source".__reservation_system_events__start_datetime AS (
	WITH year_cte AS (
		SELECT *,
			CASE
				WHEN EXTRACT(week FROM scraped_datetime) <= week_number THEN EXTRACT(YEAR FROM scraped_datetime)
				ELSE (EXTRACT(YEAR FROM scraped_datetime) + 1)
			END AS year
		FROM "source".reservation_system_events rse
	)
    SELECT
		rse.*,
	    ('Jan 1 ' || year::text || ' ' || start_time::text)::timestamptz
	        - (EXTRACT(DOW FROM (('Jan 1 ') || year::text)::date)::text || ' days')::interval
	        + (((week_number-1)*7)::text || ' days')::interval
	        + (CASE
	            WHEN day_of_week = 'Sunday' THEN 0
	            WHEN day_of_week = 'Monday' THEN 1
	            WHEN day_of_week = 'Tuesday' THEN 2
	            WHEN day_of_week = 'Wednesday' THEN 3
	            WHEN day_of_week = 'Thursday' THEN 4
	            WHEN day_of_week = 'Friday' THEN 5
	            WHEN day_of_week = 'Saturday' THEN 6
	            END::text || ' days')::interval
	        AS start_datetime
	FROM year_cte rse
	INNER JOIN "source".timeslots ts
	    ON rse.timeslot_id = ts.timeslot_id
)