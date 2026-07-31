import os


class Config:
    APP_NAME = os.getenv("APP_NAME", "URL Shortener")
    APP_ENV = os.getenv("APP_ENV", "Development")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

    SECRET_KEY = os.getenv("SECRET_KEY", "")

    HOST = "0.0.0.0"
    PORT = int(os.getenv("PORT", "5000"))
