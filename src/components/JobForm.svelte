<script lang="ts">
    import { addOneOffJob, addRecurringJob } from "../lib/api";

    let startDate = ""; // Start date
    let title = ""; // Unified title field
    let recordTime = ""; // For one-off recordings (datetime-local input)
    let startTime = ""; // For recurring recordings (time input)
    let endDate = ""; // Field for end date
    let duration = 60; // Default to 60 minutes
    let isRecurring = false; // Checkbox to toggle between one-off and recurring
    
    type DayKeys = "mon" | "tue" | "wed" | "thu" | "fri" | "sat" | "sun";

    let days: Record<DayKeys, boolean> = {
        mon: false,
        tue: false,
        wed: false,
        thu: false,
        fri: false,
        sat: false,
        sun: false,
    };

    function getSelectedDays(): string {
        return Object.keys(days)
            .filter(day => days[day as DayKeys])
            .join(",");
    }

    async function submitJob() {
        if (!title.trim()) {
            alert("Title is required.");
            return;
        }
        
        const durationInSeconds = duration * 60;

        if (isRecurring) {
            const selectedDays = getSelectedDays();
            if (!selectedDays) {
                alert("Please select at least one day for a recurring job.");
                return;
            }
            if (!startDate || !startTime) {
                alert("Please specify both start date and time for the recurring job.");
                return;
            }
            await addRecurringJob(startDate, startTime, durationInSeconds, selectedDays, title, endDate);
            alert(`Recurring job '${title}' added!`);
        } else {
            if (!recordTime) {
                alert("Please specify a date and time for the one-off job.");
                return;
            }
            await addOneOffJob(recordTime, durationInSeconds, title);
            alert(`One-off job '${title}' added!`);
        }

        // Reset form fields
        title = "";
        recordTime = "";
        startTime = "";
        startDate = "";
        duration = 60;
        endDate = "";
        days = {
            mon: false,
            tue: false,
            wed: false,
            thu: false,
            fri: false,
            sat: false,
            sun: false,
        };
    }
</script>

<h2>Schedule a Job</h2>
<form on:submit|preventDefault={submitJob} style="display: flex; flex-direction: column; gap: 1rem;">
    <!-- Job Title -->
    <div>
        <label for="title" style="font-weight: bold;">Job Title:</label>
        <input id="title" type="text" bind:value={title} placeholder="Job Title" required />
    </div>

    <!-- Recurring Job Checkbox -->
    <div>
        <label>
            <input type="checkbox" bind:checked={isRecurring} />
            Recurring Job
        </label>
    </div>

    <!-- Recurring Job Section -->
    {#if isRecurring}
        <div style="display: flex; flex-direction: column; gap: 1rem; padding: 1rem; border: 1px solid #ccc; border-radius: 8px;">
            <div style="display: flex; gap: 1rem;">
                <div>
                    <label for="start-date" style="font-weight: bold;">Start Date:</label>
                    <input id="start-date" type="date" bind:value={startDate} required />
                </div>
                <div>
                    <label for="start-time" style="font-weight: bold;">Start Time:</label>
                    <input id="start-time" type="time" bind:value={startTime} required />
                </div>
            </div>

            <fieldset>
                <legend style="font-weight: bold;">Days of the Week</legend>
                <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                    {#each Object.keys(days) as day (day)}
                        <label>
                            <input type="checkbox" bind:group={days[day as keyof typeof days]} />
                            {day.toUpperCase()}
                        </label>
                    {/each}
                </div>
            </fieldset>

            <div>
                <label for="end-date" style="font-weight: bold;">End Date:</label>
                <input id="end-date" type="date" bind:value={endDate} required />
            </div>
        </div>
    {:else}
        <!-- One-Off Job Section -->
        <div style="padding: 1rem; border: 1px solid #ccc; border-radius: 8px;">
            <label for="record-time" style="font-weight: bold;">Record Time:</label>
            <input id="record-time" type="datetime-local" bind:value={recordTime} required />
        </div>
    {/if}

    <!-- Duration -->
    <div>
        <label for="duration" style="font-weight: bold;">Duration (minutes):</label>
        <input id="duration" type="number" bind:value={duration} min="1" required />
    </div>

    <!-- Submit Button -->
    <button type="submit" style="align-self: stretch;">Schedule Job</button>
</form>
