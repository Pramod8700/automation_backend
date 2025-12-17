from google import genai
import os
from pymongo import MongoClient
import json
from dotenv import load_dotenv
from bson import ObjectId

def convert_objectid(data):
    if isinstance(data, dict):
        return {k: convert_objectid(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_objectid(i) for i in data]
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data


# 🔥 Load .env file
load_dotenv()

# ---------------- CLIENT ----------------
client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)

MODEL = "gemini-2.5-flash"


SYSTEM_PROMPT = """
You are a STRICT resume evaluation agent.

RULES:
- Output ONLY valid JSON
- Follow the schema EXACTLY
- Do NOT hallucinate missing data
- If data is missing, return empty arrays or empty strings
- Score must be between 0 and 100
- Verdict must clearly explain WHY the applicant is selected or rejected
- Use job requirements and HR priority strictly

OUTPUT SCHEMA:
{
  "verdict": "string",
  "score": number,
  "name": "string",
  "location": "string",
  "skills": ["string"],
  "experience": [
    {
      "title": "string",
      "description": "string",
      "company": "string",
      "duration": number,
      "project": {
        "title": "string",
        "description": "string",
        "link": "string"
      }
    }
  ],
  "qualifications": [
    {
      "institute": "string",
      "description": "string",
      "course": "string",
      "marks": number
    }
  ],
  "projects": [
    {
      "title": "string",
      "description": "string",
      "link": "string"
    }
  ],
  "certificates": [
    {
      "title": "string",
      "link": "string"
    }
  ],
  "social": {
    "linkedin": "string",
    "email": "string",
    "Phone": "string",
    "github": "string",
    "leetcode": "string",
    "codolio": "string",
    "codeforces": "string",
    "codechef": "string",
    "gfg": "string",
    "otherLinks": ["string"]
  }
}
"""

# ---------------- FUNCTION ----------------
def evaluate_resume(resume_text, resume_links, job, priority):
    print("new jageh")

    payload = {
        "resumeText": resume_text,
        "resumeLinks": resume_links,
        "job": job,
        "priority": priority
    }

    payload = convert_objectid(payload)  # 🔥 FIX HERE

    response = client.models.generate_content(
        model=MODEL,
        contents=[
            SYSTEM_PROMPT,
            json.dumps(payload)
        ],
        config={
            "temperature": 0.2,
            "response_mime_type": "application/json"
        }
    )

    try:
        return json.loads(response.text)
    except Exception:
        raise ValueError("Gemini returned invalid JSON")
