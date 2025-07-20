from mongoengine import connect
from app.config.db import DB
import logging

class Mongo:
    @staticmethod
    def init():
        mongo_uri=DB.MONGO_CONN_URL
        connect(host=mongo_uri)
        logging.info("Mongo DB connection successful.")