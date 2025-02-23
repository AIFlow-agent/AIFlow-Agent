import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")

    TEMP_DIR = os.getenv("TEMP_DIR", "temp") 

    @staticmethod
    def get_postgres_config():
        return {
            "dbname": Config.POSTGRES_DB,
            "user": Config.POSTGRES_USER,
            "password": Config.POSTGRES_PASSWORD,
            "host": Config.POSTGRES_HOST,
            "port": Config.POSTGRES_PORT,
        }