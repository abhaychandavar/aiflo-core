import os


class SUPPORTED_LLMS():
    GPT_3_5_TURBO = "gpt-3.5-turbo-0125"

class Settings:
    GPT_API_KEY = os.getenv("GPT_API_KEY")