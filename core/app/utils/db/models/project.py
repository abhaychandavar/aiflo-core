from enum import Enum
from mongoengine import StringField, DateTimeField, EnumField, ReferenceField
import datetime
from app.utils.db.helpers.customDocument import CustomDocument
from app.utils.db.models.user import Users

class StatusEnum(Enum):
    UNPUBLISHED = "UNPUBLISHED", 
    PUBLISHED = "PUBLISHED"


class Projects(CustomDocument):
    user = ReferenceField(Users, required=True)
    spaceID = StringField(required=True)
    name = StringField(required=True)
    description = StringField()
    status = EnumField(StatusEnum, required=True, default=StatusEnum.UNPUBLISHED)
    createdAt = DateTimeField(default=lambda: datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None))
    updatedAt = DateTimeField(default=lambda: datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None))