// server.js
const express = require('express');
const { exec } = require('child_process');
const cron = require('node-cron');
const app = express();
const PORT = 3000;

app.use(express.json());

// Store schedules in memory (or add a database if needed)
const schedules = [];

// Schedule a recording
app.post('/schedule', (req, res) => {
    const { url, startTime, endTime } = req.body;

    // Convert start and end times to cron format
    const startCron = `${startTime.minute} ${startTime.hour} * * ${startTime.dayOfWeek}`;
    const endCron = `${endTime.minute} ${endTime.hour} * * ${endTime.dayOfWeek}`;

    // Start recording
    const startJob = cron.schedule(startCron, () => {
        const fileName = `recordings/${Date.now()}.mp3`;
        const command = `ffmpeg -i "${url}" -t ${endTime - startTime} -acodec libmp3lame "${fileName}"`;
        exec(command);
    });

    // Store the job and schedule info
    schedules.push({ url, startTime, endTime, startJob });
    res.status(200).send({ message: 'Recording scheduled' });
});

app.listen(PORT, () => console.log(`Backend running on port ${PORT}`));
