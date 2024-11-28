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
    allow_origins=["*"],  # Or specify frontend origin(s), e.g., ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.start()

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

def get_filename():
    now = datetime.datetime.now()
    return now.strftime("ktcu_recording_%Y-%m-%d_%H-%M-%S.mp3")

def record_stream(duration_seconds):
    output_file = get_filename()
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

@app.post("/jobs/one-off")
def add_one_off_job(job: OneOffJob):
    scheduler.add_job(
        record_stream,
        trigger=DateTrigger(run_date=job.record_time),
        args=[job.duration],
        name=job.title,  # Use the title as the job's name
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
        args=[job.duration],
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
