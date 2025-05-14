"""
common functions used by multiple test modules
"""

def clear_starter_data(cursor):
    """
    truncates all the db tables to start with a clean slate (helpful for a few specific tests)
    """
    cursor.execute("""
        TRUNCATE TABLE "source".facilities RESTART IDENTITY CASCADE;
        TRUNCATE TABLE "source".timeslots RESTART IDENTITY CASCADE;
        TRUNCATE TABLE "source".reservation_system_events RESTART IDENTITY CASCADE;
        """)
