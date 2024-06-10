document.addEventListener("DOMContentLoaded", function() {
    var socket = io();

    // Connect to local websocket
    socket.on('connect', function() {
        $.ajax('/start_processing_video', {
            method: 'POST'
        });
    });

    /* This message is sent everytime a frame is detected to contain code. It contains the following:
    {
        code: The formatted code (string)
        explanation: An AI generated explanation of the formatted code (string)
        seconds: How many seconds into the video the frame is (number)
        timestamp: A formatted version of seconds (such as 0:25, etc.) (string)
    }
     */
    socket.on('timestampsUpdate', function(data) {
        const timestampsDiv = document.getElementById('timestamps');
        timestampsDiv.innerHTML = '';
        data.forEach(function(d) {
            const { timestamp, explanation } = d;
            const element = document.createElement('button');
            element.className = 'text-xl text-blue-400 p-2 rounded';
            element.textContent = timestamp;
            element.addEventListener('click', function() {
                alert(`Explanation for ${timestamp}: ${explanation}`);
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
