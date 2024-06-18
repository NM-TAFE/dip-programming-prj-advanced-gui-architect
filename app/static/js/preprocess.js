let timestampsArr = null;
let displayedTs = null;

function formatTimestamp(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`;
}

function setVideoPlayerTime(seconds) {
    videoPlayer.currentTime = seconds;
    progressBar.value = (seconds / videoPlayer.duration) * 100;
    const currentTimestamp = document.getElementById('currentTimestamp');
    currentTimestamp.innerHTML = formatTimestamp(seconds);
}

function previousTimestamp() {
    const currentTime = videoPlayer.currentTime;
    let closest = null;
    let closestDiff = Infinity;

    timestampsArr.forEach(ts => {
        if (Math.floor(ts.seconds) < Math.floor(currentTime)) {
            const difference = Math.abs(Math.floor(currentTime) - Math.floor(ts.seconds));
            if (difference < closestDiff) {
                closestDiff = difference;
                closest = ts;
            }
        }
    });

    if (closest) {
        setVideoPlayerTime(closest.seconds);
    }
}

function nextTimestamp() {
    const currentTime = videoPlayer.currentTime;
    let closest = null;
    let closestDiff = Infinity;

    timestampsArr.forEach(ts => {
        if (Math.floor(ts.seconds) > Math.floor(currentTime)) {
            const difference = Math.abs(Math.floor(currentTime) - Math.floor(ts.seconds));
            if (difference < closestDiff) {
                closestDiff = difference;
                closest = ts;
            }
        }
    });

    if (closest) {
        setVideoPlayerTime(closest.seconds);
    }
}

function createCapture(title, text) {
    let captureOutput = document.createElement("div");
    captureOutput.classList.add("border", "border-gray-200", "mb-2", "p-2", "pt-0", "shadow-sm", "rounded-xl", "bg-white");
    let captureTimestamp = document.createElement("span");
    captureTimestamp.innerHTML = title;
    let captureTitle = document.createElement("p");
    captureTitle.classList.add("text-gray-400", "text-xs", "flex", "justify-between", "border-b", "border-gray-200", "py-1");
    let captureBody = document.createElement("code");
    captureBody.id = "code_" + nextCodeId++;
    let copyThisCapture = document.createElement("button");
    copyThisCapture.innerHTML = "Open in IDE";
    copyThisCapture.classList.add("text-purple-600", "hover:cursor-pointer", "underline");
    copyThisCapture.onclick = () =>  openInIde(captureBody.id);
    captureTitle.appendChild(captureTimestamp);
    captureTitle.appendChild(copyThisCapture);
    captureOutput.appendChild(captureTitle);
    let captureBodyWrap = document.createElement("pre");
    captureBodyWrap.classList.add("overflow-x-auto");
    captureBody.classList.add("w-full", "whitespace-pre", "language-python", "text-xs");
    captureBody.contentEditable = "true";
    let tempDiv = document.createElement("div");
    tempDiv.innerHTML = text;
    let decodedText = tempDiv.textContent;
    captureBody.appendChild(document.createTextNode(decodedText));
    captureBodyWrap.appendChild(captureBody);
    captureOutput.appendChild(captureBodyWrap);
    captureOutputContainer.appendChild(captureOutput);
}

function updateDisplayedCodeTimestamps(currentTime) {
    if (!timestampsArr || timestampsArr.length === 0) return;

    for (let i = timestampsArr.length - 1; i >= 0; i--) {
        const ts = timestampsArr[i];
        const { seconds, code } = ts;

        if ((seconds - 1) <= currentTime) {
            if (String(displayedTs?.seconds) !== String(seconds)) {
                captureOutputContainer.innerHTML = '';
                displayedTs = ts;
                createCapture(`Detected @ Timestamp: ${formatTimestamp(seconds)}`, code);
            }

            return;
        }
    }
}

videoPlayer.addEventListener("timeupdate", (event) => {
    updateDisplayedCodeTimestamps(videoPlayer.currentTime);
});

document.addEventListener("DOMContentLoaded", function() {
    const socket = io();

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
        timestampsArr = data;
        // captureOutputContainer.innerHTML = '';
        data.forEach(function(d) {
            const { seconds, code, explanation } = d;
            const timestamp = formatTimestamp(seconds);
            const element = document.createElement('button');
            element.className = 'text-xl text-blue-400 p-2 rounded';
            element.textContent = timestamp;
            timestampsDiv.appendChild(element);

            // if (code) {
            //     createCapture("Detected @ Timestamp: " + timestamp, code);
            // }

            element.addEventListener('click', function() {
                setVideoPlayerTime(seconds);
                updateDisplayedCodeTimestamps(videoPlayer.currentTime);
            });
        });
    });

    // This message is sent everytime a frame has finished being examined
    socket.on('processingProgressUpdate', function(progress) {
        const processingText = document.getElementById('processingText');
        processingText.textContent = `Your video is currently processing... (${progress})`;
    });

    // Sent once the processing is complete
    socket.on('finishedProcessing', function(full_code) {
        const processingText = document.getElementById('processingText');
        const processingSubtext = document.getElementById('processingSubtext');
        processingText.textContent = "Your video has finished processing!";
        processingSubtext.textContent = "All timestamps detected to contain code are listed below.";
        if (full_code && typeof full_code === "string") {
            createCapture("Final Code", full_code);
        }
    });
});