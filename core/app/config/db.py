import os
class DB:
    MONGO_CONN_URL=os.getenv("MONGO_CONN_URL", "mongodb+srv://<user>:<password>@<host>.mongodb.net/<db-name>")

db = DB()