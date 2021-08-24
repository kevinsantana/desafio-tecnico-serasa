__version__ = "0.0.1"

from user_api.database import create_database


create_database(reset=False)
