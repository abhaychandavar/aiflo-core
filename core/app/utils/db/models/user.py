from enum import Enum
from mongoengine import StringField, DateTimeField, BooleanField, EnumField
import datetime
from app.utils.parser import mongo_to_dict
from app.utils.db.helpers.customDocument import CustomDocument
class AuthMethods(Enum):
    EMAIL_PASS = "email-pass", 
    GOOGLE_AUTH = "google-oauth"
class Users(CustomDocument):
    name = StringField()
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    imageURL = StringField()
    authMethod = EnumField(AuthMethods, required=True)
    isActive = BooleanField(default=True)
    createdAt = DateTimeField(default=lambda: datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None))
    updatedAt = DateTimeField(default=lambda: datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None))
