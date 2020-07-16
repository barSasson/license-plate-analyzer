import datetime
from peewee import SqliteDatabase, Model, TextField, TimestampField, BooleanField

DB_LOCAL_PATH = 'parking_lot.db'
db = SqliteDatabase(None)


class CarEntry(Model):
    license_plate = TextField()
    timestamp = TimestampField(index=True, unique=True, utc=True)
    is_allowed = BooleanField()
    is_public_transportation = BooleanField()
    is_military_or_law_enforcement = BooleanField()
    has_no_letters = BooleanField()

    class Meta:
        database = db


class ParkingLotLoggingDB(object):
    def __init__(self, connected_database):
        self._connected_db = connected_database

    @classmethod
    def from_file_path(cls, filepath: str = DB_LOCAL_PATH):
        db.init(filepath)
        db.connect()
        db.create_tables([CarEntry])
        return cls(db)

    @staticmethod
    def insert_car_entry(license_plate,
                         is_public_transportation,
                         is_military_or_law_enforcement,
                         has_no_letters, is_allowed):
        entry = CarEntry(timestamp=datetime.datetime.utcnow(),
                         license_plate=license_plate,
                         is_military_or_law_enforcement=is_military_or_law_enforcement,
                         is_public_transportation=is_public_transportation,
                         has_no_letters=has_no_letters,
                         is_allowed=is_allowed)
        entry.save()
        return True

    def close(self):
        self._connected_db.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()
