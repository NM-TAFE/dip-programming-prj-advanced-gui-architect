function formatTimestamp(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`;
}

document.addEventListener("DOMContentLoaded", function() {
    var videoPlayer = document.getElementById("videoPlayer");
    var progressBar = document.getElementById("progressBar");
    var socket = io();

    // Connect to local websocket
    socket.on('connect', function() {
        $.ajax('/start_processing_video', {
            method: 'POST'
        });
    });

    /* This message is sent everytime a frame is detected to contain code. It contains an array full of the following:
    {
        code: The formatted code (string | null)
        explanation: An AI generated explanation of the formatted code (string | null)
        seconds: How many seconds into the video the frame is (number)
    }
     */
    socket.on('timestampsUpdate', function(data) {
        const timestampsDiv = document.getElementById('timestamps');
        timestampsDiv.innerHTML = '';
        data.forEach(function(d) {
            const { seconds, explanation } = d;
            const timestamp = formatTimestamp(seconds);
            const element = document.createElement('button');
            element.className = 'text-xl text-blue-400 p-2 rounded';
            element.textContent = timestamp;
            element.addEventListener('click', function() {
                videoPlayer.currentTime = seconds;
                progressBar.value = (seconds / videoPlayer.duration) * 100;
                const currentTimestamp = document.getElementById('currentTimestamp');
                currentTimestamp.innerHTML = formatTimestamp(seconds);
                console.log(`Code explanation for ${timestamp}: ${explanation}`);
            });
            timestampsDiv.appendChild(element);
        });
    });

    // This message is sent everytime a frame has finished being examined
    socket.on('processingProgressUpdate', function(progress) {
        const processingText = document.getElementById('processingText');
        processingText.textContent = `Your video is currently processing... (${progress})`;
    });

    // Sent once the processing is complete
    socket.on('finishedProcessing', function() {
        const processingText = document.getElementById('processingText');
        const processingSubtext = document.getElementById('processingSubtext');
        processingText.textContent = "Your video has finished processing!";
        processingSubtext.textContent = "All timestamps detected to contain code are listed below.";
    });
});
