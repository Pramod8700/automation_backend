import time
from bson import ObjectId
from db import (
    reports_collection,
    applicants_collection,
    resumes_collection,
    jobs_collection
)
from agent import evaluate_resume

print("Worker started")

while True:
    report = reports_collection.find_one({"status": "PENDING"})
    if not report:
        print("No pending reports")
        time.sleep(10)
    report_id = report["_id"]
    #reports_collection.find_one_and_update({"_id":report_id},{"status":"PROCESSING"})
    print("Processing Report:", report_id)
    priority=report["priority"]
    applicants=report["results"]
    job_id=report["jobProfile"]
    job=jobs_collection.find_one({"_id": job_id})
    title=job["title"]
    description=job["description"]
    skillRequired=job["skillRequired"]
    experienceRequired=job["experienceRequired"]
    vacancies=job["vacancies"]
    location=job["location"]
    print("job")
    for applicant_id in applicants:
        applicant=applicants_collection.find_one({"_id": applicant_id})
        #applicants_collection.find_one_and_update({"_id":applicant_id},{"status":"PROCESSING"})
        resume_id=applicant["resume"]
        resume=resumes_collection.find_one({"_id":resume_id})
        print("aagaye hum")
        extracted=resume["extracted"]
        text=extracted["text"]
        link=extracted["links"]
        try:
            print("yeha aa gaye h hum")
            
            response=  evaluate_resume(resume_text=text,resume_links=link,job={title,description,experienceRequired,skillRequired,location,vacancies},priority=priority)
            print("call me baby")
            print(response)
            #applicants_collection.find_one_and_update({"_id":applicant_id},{"verdict":response["verdict"],"score":response["score"],"name":response["name"],"location":response["location"],"skills":response["skills"],"experience":response["experience"],"qualifications":response["qualifications"],"projects":response["projects"],"certificates":response["certificates"],"social":response["social"]})
            exit(1)
        except Exception as e:
            print(e)
    




    # reports_collection.update_one(
    #     {"_id": report_id},
    #     {"$set": {"status": "PROCESSING"}}
    # )
    # applicants = list(applicants_collection.find({
    #     "createdFor": report_id,
    #     "status": "PENDING"
    # }))

    # if not applicants:
    #     print("No applicants for report")
    #     reports_collection.update_one(
    #         {"_id": report_id},
    #         {"$set": {"status": "DONE"}}
    #     )
    #     continue

    # job = jobs_collection.find_one({"_id": report["jobProfile"]})

    # for applicant in applicants:
    #     applicant_id = applicant["_id"]
    #     print("Evaluating Applicant:", applicant_id)

    #     try:
    #         resume = resumes_collection.find_one(
    #             {"_id": applicant["resume"]}
    #         )

    #         resume_text = resume.get("extracted", {}).get("text", "")
    #         if not resume_text:
    #             raise Exception("Empty resume text")

    #         result = evaluate_resume(resume_text, job)

    #         applicants_collection.update_one(
    #             {"_id": applicant_id},
    #             {
    #                 "$set": {
    #                     "score": result["score"],
    #                     "verdict": result["verdict"],
    #                     "failureReason": result["reason"],
    #                     "status": "UNVERIFIED"
    #                 }
    #             }
    #         )

    #     except Exception as e:
    #         applicants_collection.update_one(
    #             {"_id": applicant_id},
    #             {
    #                 "$set": {
    #                     "status": "FAILED",
    #                     "failureReason": str(e),
    #                     "score": 0,
    #                     "verdict": "REJECTED"
    #                 }
    #             }
    #         )

    # reports_collection.update_one(
    #     {"_id": report_id},
    #     {"$set": {"status": "DONE"}}
    # )

    # print("Report completed:", report_id)
