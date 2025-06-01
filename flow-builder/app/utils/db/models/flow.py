from enum import Enum
from mongoengine import StringField, DateTimeField, ObjectIdField, DictField, EnumField, ReferenceField
import datetime
from app.utils.parser import mongo_to_dict
from app.utils.db.helpers.customDocument import CustomDocument
from app.utils.db.models.user import Users

class StatusEnum(Enum):
    UNPUBLISHED = "UNPUBLISHED", 
    PUBLISHED = "PUBLISHED"


class Flows(CustomDocument):
    user = ReferenceField(Users, required=True)
    name = StringField(required=True, unique=True)
    description = StringField()
    flow = DictField()
    status = EnumField(StatusEnum, required=True, default=StatusEnum.UNPUBLISHED)
    createdAt = DateTimeField(default=lambda: datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None))
    updatedAt = DateTimeField(default=lambda: datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None))