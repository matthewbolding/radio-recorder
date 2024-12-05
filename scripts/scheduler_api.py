import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from pydantic import BaseModel
import subprocess
import datetime

# Initialize the FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# File to persist jobs
JOBS_FILE = "jobs.json"

# Stream URL
STREAM_URL = "https://ktcustream.tcu.edu"

class OneOffJob(BaseModel):
    record_time: datetime.datetime
    duration: int
    title: str

class RecurringJob(BaseModel):
    start_date: datetime.date
    start_time: datetime.time
    duration: int
    days_of_week: str
    title: str
    end_date: datetime.date

def get_filename(title):
    now = datetime.datetime.now()
    safe_title = title.replace(" ", "_").replace("/", "-")
    return now.strftime(f"recordings/{safe_title}_%Y-%m-%d_%H-%M.mp3")

def record_stream(duration_seconds, title):
    output_file = get_filename(title)
    print(f"Recording to {output_file} for {duration_seconds} seconds...")
    try:
        subprocess.run([
            "ffmpeg", "-i", STREAM_URL,
            "-t", str(duration_seconds),
            "-acodec", "libmp3lame",
            "-b:a", "128k",
            output_file
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Recording failed: {e}")


def save_jobs_to_disk():
    jobs = []
    for job in scheduler.get_jobs():
        # Serialize trigger for DateTrigger or CronTrigger
        if isinstance(job.trigger, DateTrigger):
            trigger = job.trigger.run_date.isoformat()
        elif isinstance(job.trigger, CronTrigger):
            # Convert CronTrigger fields into a serializable dictionary
            trigger = {
                "type": "cron",
                **{field.name: str(field) for field in job.trigger.fields},
            }
        else:
            trigger = str(job.trigger)

        jobs.append({
            "id": job.id,
            "name": job.name,
            "trigger": trigger,
            "args": job.args,
            "kwargs": {},  # Add additional custom args here if needed
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None
        })

    # Write jobs to file
    with open(JOBS_FILE, "w") as f:
        json.dump(jobs, f, indent=4)
    print(f"Saved {len(jobs)} jobs to {JOBS_FILE}")

def load_jobs_from_disk():
    if not os.path.exists(JOBS_FILE):
        print(f"No jobs file found at {JOBS_FILE}.")
        return

    with open(JOBS_FILE, "r") as f:
        jobs = json.load(f)

    for job in jobs:
        try:
            # Handle triggers based on type
            if isinstance(job["trigger"], str) and "T" in job["trigger"]:
                # ISO 8601 format for DateTrigger
                run_date = datetime.datetime.fromisoformat(job["trigger"])
                trigger = DateTrigger(run_date=run_date)
            elif isinstance(job["trigger"], dict) and job["trigger"].get("type") == "cron":
                # Recreate CronTrigger
                cron_fields = {key: value for key, value in job["trigger"].items() if key != "type"}
                trigger = CronTrigger(**cron_fields)
            else:
                print(f"Unknown trigger format: {job['trigger']}")
                continue

            # Re-add the job to the scheduler
            scheduler.add_job(
                record_stream,
                trigger=trigger,
                args=job["args"],
                name=job["name"]
            )
            print(f"Restored job: {job['name']}")
        except Exception as e:
            print(f"Failed to restore job {job['name']}: {e}")

    print(f"Loaded {len(jobs)} jobs from {JOBS_FILE}")


@app.on_event("startup")
def startup_event():
    load_jobs_from_disk()

@app.on_event("shutdown")
def shutdown_event():
    save_jobs_to_disk()

@app.post("/jobs/one-off")
def add_one_off_job(job: OneOffJob):
    scheduler.add_job(
        record_stream,
        trigger=DateTrigger(run_date=job.record_time),
        args=[job.duration, job.title],
        name=job.title,
        replace_existing=True
    )
    return {"message": f"One-off job '{job.title}' scheduled for {job.record_time}"}

@app.post("/jobs/recurring")
def add_recurring_job(job: RecurringJob):
    scheduler.add_job(
        record_stream,
        trigger=CronTrigger(
            start_date=job.start_date,
            day_of_week=job.days_of_week,
            hour=job.start_time.hour,
            minute=job.start_time.minute,
            end_date=job.end_date
        ),
        args=[job.duration, job.title],
        name=job.title,
        replace_existing=True
    )
    return {"message": f"Recurring job '{job.title}' scheduled for {job.start_time} on {job.days_of_week} until {job.end_date}"}

@app.get("/jobs")
def list_jobs():
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run_time": job.next_run_time
        })
    return jobs

@app.delete("/jobs/{job_id}")
def delete_job(job_id: str):
    try:
        scheduler.remove_job(job_id)
        return {"message": f"Job {job_id} deleted"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found: {str(e)}")
