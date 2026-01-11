import os

class Config:
    PORT = int(os.environ.get("PORT", 8080))
    DEBUG = False
    TESTING = False

class TestConfig(Config):
    TESTING = True
    DEBUG = True
