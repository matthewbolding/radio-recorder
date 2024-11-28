/**
 * Add a one-off job.
 * @param {string} record_time - The time to start recording (ISO 8601 format).
 * @param {number} duration - Duration of the recording in seconds.
 * @param {string} title - The job's title.
 */
export async function addOneOffJob(record_time: string, duration: number, title: string) {
    const response = await fetch("http://127.0.0.1:8000/jobs/one-off", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ record_time, duration, title }),
    });
    return response.json();
}

/**
 * Add a recurring job.
 * @param {string} start_date - The earliers possible day of a recording,
 * @param {string} start_time - The time of day to start recording (HH:mm).
 * @param {number} duration - Duration of the recording in seconds.
 * @param {string} days_of_week - Days of the week to record (e.g., "mon,wed,fri").
 * @param {string} title - The job's title.
 */
export async function addRecurringJob(
    start_date: string,
    start_time: string,
    duration: number,
    days_of_week: string,
    title: string,
    end_date: string
): Promise<any> {
    const response = await fetch("http://127.0.0.1:8000/jobs/recurring", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ start_date, start_time, duration, days_of_week, title, end_date }),
    });
    return response.json();
}

/**
 * List all scheduled jobs.
 * @returns {Promise<Array<{ id: string, name: string, next_run_time: string }>>}
 */
export async function listJobs(): Promise<{ id: string; name: string; next_run_time: string }[]> {
    const response = await fetch("http://127.0.0.1:8000/jobs");
    return response.json();
}

/**
 * Delete a job by ID.
 * @param {string} job_id - The ID of the job to delete.
 */
export async function deleteJob(job_id: string): Promise<any> {
    const response = await fetch(`http://127.0.0.1:8000/jobs/${job_id}`, {
        method: "DELETE",
    });
    return response.json();
}
