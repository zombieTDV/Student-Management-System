from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
from dotenv import load_dotenv

load_dotenv()


class Database:
    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        """Singleton pattern - only one database connection"""
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            self.connect()

    def connect(self):
        """Connect to MongoDB"""
        try:
            # MongoDB Atlas (Cloud)
            MONGO_URL = os.getenv("MONGO_URL")
            MONGO_DB = os.getenv("MONGO_DB")
            self._client = MongoClient(MONGO_URL)

            # Test connection
            self._client.admin.command("ping")
            print("✅ Connected to MongoDB successfully!")

            # Select database
            self._db = self._client[MONGO_DB]  # Database name

        except ConnectionFailure as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            raise

    def get_db(self):
        """Get database instance"""
        if self._db is None:
            self.connect()
        return self._db

    def close(self):
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            print("MongoDB connection closed")


# Create global database instance
db = Database()
