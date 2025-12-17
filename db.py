from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI not found in .env")

client = MongoClient(MONGO_URI)
db = client.get_database()

print("MongoDB Connected")
print("DB NAME:", db.name)

reports_collection = db["reports"]
applicants_collection = db["applicants"]
resumes_collection = db["resumes"]
jobs_collection = db["jobs"]

