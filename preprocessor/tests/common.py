def clear_starter_data(cursor):
    cursor.execute("""
        TRUNCATE TABLE "source".facilities RESTART IDENTITY CASCADE;
        TRUNCATE TABLE "source".timeslots RESTART IDENTITY CASCADE;
        TRUNCATE TABLE "source".reservation_system_events RESTART IDENTITY CASCADE;
        """)