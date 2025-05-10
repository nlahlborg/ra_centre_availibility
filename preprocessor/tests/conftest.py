"""
start mock dbs for all tests
"""
from pathlib import Path
from pytest_postgresql import factories

postgresql_local_dev = factories.postgresql_noproc(
    user='postgres',
    password='postgres',
    load=[
        Path(__file__).parent / "helpers" / "helper_helper_loaded_objects.sql",
        Path(__file__).parent / "helpers" / "helper_helper_loaded_objects_blank.sql",
        Path(__file__).parent / "helpers" / "source_facilities.sql",
        Path(__file__).parent / "helpers" / "source_timeslots.sql",
        Path(__file__).parent / "helpers" / "source_reservation_system_events.sql"
        ]
    )
conn_fixture = factories.postgresql("postgresql_local_dev", dbname="test")
