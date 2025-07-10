import os
from typing import TypedDict

class SUPPORTED_LLMS():
    GPT_3_5_TURBO = {
            "id": "gpt-3.5-turbo-0125",
            "name": "GPT 3.5 Turbo"
        }

    @classmethod
    def get_models_dict(cls):
        """Return all LLM models as a dictionary with attribute names as keys"""
        models = {}
        for attr_name in dir(cls):
            if not attr_name.startswith('_') and not callable(getattr(cls, attr_name)):
                attr_value = getattr(cls, attr_name)
                if isinstance(attr_value, dict) and 'id' in attr_value and 'name' in attr_value:
                    models[attr_name] = attr_value
        return models

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")