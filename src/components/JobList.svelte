<script lang="ts">
    import { listJobs, deleteJob } from "../lib/api";
    import { format } from "date-fns";

    type Job = {
        id: string;
        name: string;
        next_run_time: string;
    };

    let jobs: Job[] = [];

    async function fetchJobs() {
        jobs = await listJobs();
    }

    async function removeJob(id: string) {
        await deleteJob(id);
        await fetchJobs();
    }

    // Format the next run time
    function formatNextRunTime(nextRunTime: string) {
        if (!nextRunTime) return "No scheduled run";
        return format(new Date(nextRunTime), "PPpp"); // e.g., Jan 1, 2024, 2:00 PM
    }

    fetchJobs();
</script>

<h2>Scheduled Jobs</h2>
<ul>
    {#each jobs as job}
        <li>
            <strong>Title:</strong> {job.name} <br>
            <strong>Next Run:</strong> {formatNextRunTime(job.next_run_time)} <br>
            <button on:click={() => removeJob(job.id)}>Delete</button>
        </li>
    {/each}
</ul>