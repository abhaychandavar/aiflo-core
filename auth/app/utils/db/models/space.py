from enum import Enum
from mongoengine import StringField, DateTimeField, ReferenceField
import datetime
from app.utils.parser import mongo_to_dict
from app.utils.db.helpers.customDocument import CustomDocument
from app.utils.db.models.user import Users

class Spaces(CustomDocument):
    name = StringField()
    user = ReferenceField(Users, required=True)
    createdAt = DateTimeField(default=lambda: datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None))
    updatedAt = DateTimeField(default=lambda: datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None))
