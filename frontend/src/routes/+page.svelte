<script>
    import { onMount } from 'svelte';
    let url = '';
    let startTime = '';
    let endTime = '';

    async function scheduleRecording() {
        await fetch('http://localhost:3000/schedule', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, startTime, endTime })
        });
    }
</script>

<form on:submit|preventDefault={scheduleRecording}>
    <p>Stream URL:</p>
    <input type="text" bind:value={url} />

    <p>Start Time (HH:MM):</p>
    <input type="time" bind:value={startTime} />

    <p>End Time (HH:MM):</p>
    <input type="time" bind:value={endTime} />

    <button type="submit">Schedule Recording</button>
</form>
