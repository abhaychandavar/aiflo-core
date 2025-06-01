from mongoengine import Document
from app.utils.parser import mongo_to_dict

class CustomDocument(Document):
    meta = {
        'abstract': True
    }
    def to_dict(self):
        return mongo_to_dict(self.to_mongo())
    
    