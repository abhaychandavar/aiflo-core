from enum import Enum
from mongoengine import DateTimeField, StringField, EnumField, FloatField
import datetime
from app.utils.db.helpers.customDocument import CustomDocument

class KnowledgeBaseType(Enum):
        SEQUENTIAL = 'sequential'

class KnowledgeBase(CustomDocument):
    refID = StringField(required=True, unique=True)
    key = StringField(required=True)
    size = FloatField(required=True)
    fileExt = StringField(required=True)
    fileName = StringField(required=True)
    flowID = StringField(required=True)
    nodeID = StringField(required=True)
    path   = StringField(required=True)
    uploadedAt = DateTimeField()
    processedAt = DateTimeField()
    type = EnumField(KnowledgeBaseType)
    createdAt = DateTimeField(default=lambda: datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None))
    updatedAt = DateTimeField(default=lambda: datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None))
