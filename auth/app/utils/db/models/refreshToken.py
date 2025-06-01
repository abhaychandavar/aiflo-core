from enum import Enum
from mongoengine import StringField, DateTimeField, ObjectIdField
import datetime
from app.utils.parser import mongo_to_dict
from app.utils.db.helpers.customDocument import CustomDocument

class RefreshTokens(CustomDocument):
    user = ObjectIdField(required=True)
    token = StringField(required=True)
    createdAt = DateTimeField(default=lambda: datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None))
    updatedAt = DateTimeField(default=lambda: datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None))

    meta = {
        'indexes': [
            {
                'fields': ['createdAt'],
                'expireAfterSeconds': 604800
            }
        ]
    }