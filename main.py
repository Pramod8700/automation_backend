from fastapi import FastAPI
import asyncio
from bson import ObjectId
from db import (
    reports_collection,
    applicants_collection,
    resumes_collection,
    jobs_collection
)
from agent import evaluate_resume

app = FastAPI(title="ATS Web Service")

async def worker_loop():
    print("Worker started (inside FastAPI)")
    await asyncio.sleep(3)  # wait for startup

    while True:
        # Pick one pending report
        report = reports_collection.find_one_and_update(
            {"status": "PENDING"},
            {"$set": {"status": "PROCESSING"}}
        )

        if not report:
            print("No pending reports")
            await asyncio.sleep(10)
            continue

        report_id = report["_id"]
        print("Processing Report:", report_id)

        priority = report.get("priority")
        applicant_ids = report.get("results", [])
        job_id = report.get("jobProfile")

        job = jobs_collection.find_one({"_id": job_id})
        if not job:
            reports_collection.update_one(
                {"_id": report_id},
                {"$set": {"status": "FAILED"}}
            )
            continue

        job_payload = {
            "title": job.get("title", ""),
            "description": job.get("description", ""),
            "skillRequired": job.get("skillRequired", []),
            "experienceRequired": job.get("experienceRequired", 0),
            "vacancies": job.get("vacancies", 0),
            "location": job.get("location", "")
        }

        try:
            for applicant_id in applicant_ids:
                applicant = applicants_collection.find_one({"_id": applicant_id})
                if not applicant:
                    continue

                resume_id = applicant.get("resume")
                resume = resumes_collection.find_one({"_id": resume_id})
                if not resume:
                    applicants_collection.update_one(
                        {"_id": applicant_id},
                        {"$set": {"status": "FAILED", "failureReason": "Resume not found"}}
                    )
                    continue

                extracted = resume.get("extracted", {})
                text = extracted.get("text", "")
                links = extracted.get("links", [])

                applicants_collection.update_one(
                    {"_id": applicant_id},
                    {"$set": {"status": "PROCESSING"}}
                )

                response = evaluate_resume(
                    resume_text=text,
                    resume_links=links,
                    job=job_payload,
                    priority=priority
                )

                if not response:
                    applicants_collection.update_one(
                        {"_id": applicant_id},
                        {"$set": {"status": "FAILED", "failureReason": "Empty AI response"}}
                    )
                    continue

                applicants_collection.update_one(
                    {"_id": applicant_id},
                    {
                        "$set": {
                            "verdict": response.get("verdict"),
                            "score": response.get("score"),
                            "name": response.get("name"),
                            "location": response.get("location"),
                            "skills": response.get("skills", []),
                            "experience": response.get("experience", []),
                            "qualifications": response.get("qualifications", []),
                            "projects": response.get("projects", []),
                            "certificates": response.get("certificates", []),
                            "social": response.get("social", {}),
                            "status": "UNVERIFIED"
                        }
                    }
                )

            reports_collection.update_one(
                {"_id": report_id},
                {"$set": {"status": "DONE"}}
            )

            print("Report completed:", report_id)

        except Exception as e:
            print("Worker error:", e)
            reports_collection.update_one(
                {"_id": report_id},
                {"$set": {"status": "FAILED"}}
            )

        await asyncio.sleep(2)

@app.on_event("startup")
async def start_worker():
    asyncio.create_task(worker_loop())

@app.get("/")
def health():
    return {"status": "ATS Web Service Running"}
