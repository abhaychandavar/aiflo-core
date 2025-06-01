from os import getenv
class DB:
    MONGO_CONN_URL=getenv("MONGO_CONN_URL", "mongodb+srv://<user>:<password>@<host>.mongodb.net/<db-name>")

db = DB()