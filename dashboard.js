let currentElapsedSeconds = 0;
let isActive = false;

let breakElapsedSeconds = 0;
let isBreakActive = false;

function formatDuration(totalSeconds) {
totalSeconds = Math.max(0, Math.floor(totalSeconds));


const hours = Math.floor(totalSeconds / 3600);
const minutes = Math.floor((totalSeconds % 3600) / 60);
const seconds = totalSeconds % 60;

return (
    String(hours).padStart(2, "0") +
    ":" +
    String(minutes).padStart(2, "0") +
    ":" +
    String(seconds).padStart(2, "0")
);


}

function parseDate(value) {
if (!value) return null;


const date = new Date(
    value.replace(" ", "T")
);

if (Number.isNaN(date.getTime())) {
    return null;
}

return date;


}

function formatDateTime(value) {
const date = parseDate(value);


if (!date) return "--";

return date.toLocaleString();


}

function formatDate(value) {
const date = parseDate(value);


if (!date) return "--";

return date.toLocaleDateString();


}

function formatTime(value) {
const date = parseDate(value);

if (!date) return "--";

return date.toLocaleTimeString([], {
    hour: "numeric",
    minute: "2-digit",
    second: "2-digit"
});

}

async function loadStatus() {


try {

    const response = await fetch(
        "/api/status"
    );

    if (!response.ok) {
        throw new Error(
            "Status request failed"
        );
    }

    const data = await response.json();

    isActive =
        data.status === "ACTIVE";

    currentElapsedSeconds =
        data.elapsed_seconds || 0;

    document.getElementById(
        "workerName"
    ).textContent =
        data.name || "--";

    document.getElementById(
        "workerId"
    ).textContent =
        data.worker_id || "--";

    document.getElementById(
        "signInTime"
    ).textContent =
        formatDateTime(
            data.sign_in
        );

    const statusText =
        document.getElementById(
            "statusText"
        );

    const indicator = document.getElementById("statusIndicator");

    const rfidIndicator =
    document.querySelector(
        ".rfid-indicator"
    );

const rfidSlider =
    document.getElementById(
        "rfidStatusSlider"
    );

const rfidStatusText =
    document.getElementById(
        "rfidStatusText"
    );

    if (isActive) {

    statusText.textContent =
        "SIGNED IN";

    rfidIndicator.classList.add(
        "active"
    );

    rfidStatusText.textContent =
        "Card Connected";

        indicator.textContent =
            "●";

        indicator.className =
            "status-indicator active";

    } else {

        statusText.textContent =
            "SIGNED OUT";
	rfidIndicator.classList.remove(
	    "active"
	);

	rfidStatusText.textContent =
   	   "Card Disconnected";

        indicator.textContent =
            "●";

        indicator.className =
            "status-indicator off";

    }

    updateElapsedDisplay();

    updateBreakButtonState();

} catch (error) {

    console.error(error);

    document.getElementById(
        "statusText"
    ).textContent =
        "Connection Error";
}


}

function updateElapsedDisplay() {


document.getElementById(
    "elapsedTime"
).textContent =
    formatDuration(
        currentElapsedSeconds
    );

}

async function loadBreakStatus() {

try {

    const response = await fetch(
        "/api/break/status"
    );

    if (!response.ok) {
        throw new Error(
            "Break status request failed"
        );
    }

    const data =
        await response.json();

    isBreakActive =
        data.break_status === "ACTIVE";

    breakElapsedSeconds =
        data.elapsed_seconds || 0;

    const breakStatusText =
        document.getElementById(
            "breakStatusText"
        );

    if (isBreakActive) {

        breakStatusText.textContent =
            "ON BREAK";

    } else {

        breakStatusText.textContent =
            "No Break";

        breakElapsedSeconds = 0;
    }

    document.getElementById(
        "breakElapsedTime"
    ).textContent =
        formatDuration(
            breakElapsedSeconds
        );

    updateBreakButtonState();

} catch (error) {

    console.error(error);
}


}

function updateBreakButtonState() {

const startButton =
    document.getElementById(
        "startBreakButton"
    );

const endButton =
    document.getElementById(
        "endBreakButton"
    );

if (!startButton || !endButton) {
    return;
}

if (!isActive) {

    startButton.disabled = true;
    endButton.disabled = true;

    return;
}

if (isBreakActive) {

    startButton.disabled = true;
    endButton.disabled = false;

} else {

    startButton.disabled = false;
    endButton.disabled = true;
}


}

async function startBreak() {


if (!isActive) {
    return;
}

const button =
    document.getElementById(
        "startBreakButton"
    );

button.disabled = true;

try {

    const response = await fetch(
        "/api/break/start",
        {
            method: "POST"
        }
    );

    if (!response.ok) {
        throw new Error(
            "Start break request failed"
        );
    }

    const data =
        await response.json();

    if (!data.success) {

        alert(
            data.message ||
            "Unable to start break."
        );

        return;
    }

    await loadBreakStatus();
    await updateBreakSummary();

} catch (error) {

    console.error(error);

    alert(
        "Unable to start break."
    );

} finally {

    updateBreakButtonState();
}


}

async function endBreak() {

if (!isBreakActive) {
    return;
}

const button =
    document.getElementById(
        "endBreakButton"
    );

button.disabled = true;

try {

    const response = await fetch(
        "/api/break/end",
        {
            method: "POST"
        }
    );

    if (!response.ok) {
        throw new Error(
            "End break request failed"
        );
    }

    const data =
        await response.json();

    if (!data.success) {

        alert(
            data.message ||
            "Unable to end break."
        );

        return;
    }

    await loadBreakStatus();
    await updateBreakSummary();

} catch (error) {

    console.error(error);

    alert(
        "Unable to end break."
    );

} finally {

    updateBreakButtonState();
}


}

async function updateBreakSummary() {


try {

    const response = await fetch(
        "/api/summary"
    );

    if (!response.ok) {
        throw new Error(
            "Summary request failed"
        );
    }

    const data =
        await response.json();

    document.getElementById(
        "breakTotal"
    ).textContent =
        formatDuration(
            data.break_today_seconds || 0
        );

} catch (error) {

    console.error(error);
}


}

function tickTimer() {


if (isActive) {

    currentElapsedSeconds++;

    updateElapsedDisplay();
}

if (isBreakActive) {

    breakElapsedSeconds++;

    document.getElementById(
        "breakElapsedTime"
    ).textContent =
        formatDuration(
            breakElapsedSeconds
        );
}


}

async function loadHistory() {


const historyBody =
    document.getElementById(
        "historyBody"
    );

try {

    const response = await fetch(
        "/api/history"
    );

    if (!response.ok) {
        throw new Error(
            "History request failed"
        );
    }

    const data =
        await response.json();

    const sessions =
        data.sessions || [];

    if (sessions.length === 0) {

        historyBody.innerHTML = `
            <tr>
                <td colspan="5" class="loading">
                    No work sessions recorded yet.
                </td>
            </tr>
        `;

        await updateTotals();

        return;
    }

    historyBody.innerHTML = "";

    sessions.forEach(
        session => {

            const row =
                document.createElement(
                    "tr"
                );

            const statusClass =
                session.status === "ACTIVE"
                    ? "status-active"
                    : "status-completed";

            row.innerHTML = `
                <td>${formatDate(
                    session.sign_in
                )}</td>

                <td>${formatTime(
                    session.sign_in
                )}</td>

                <td>${formatTime(
                    session.sign_out
                )}</td>

                <td>${formatDuration(
                    session.duration_seconds || 0
                )}</td>

                <td class="${statusClass}">
                    ${session.status}
                </td>
            `;

            historyBody.appendChild(
                row
            );
        }
    );

    await updateTotals();

} catch (error) {

    console.error(error);

    historyBody.innerHTML = `
        <tr>
            <td colspan="5" class="loading">
                Unable to load session history.
            </td>
        </tr>
    `;
}

}

async function updateTotals() {

try {

    const response = await fetch(
        "/api/summary"
    );

    if (!response.ok) {
        throw new Error(
            "Summary request failed"
        );
    }

    const data =
        await response.json();

    document.getElementById(
        "todayTotal"
    ).textContent =
        formatDuration(
            data.today_seconds || 0
        );

    document.getElementById(
        "weekTotal"
    ).textContent =
        formatDuration(
            data.week_seconds || 0
        );

    document.getElementById(
        "monthTotal"
    ).textContent =
        formatDuration(
            data.month_seconds || 0
        );

document.getElementById(
    "netTodayTotal"
).textContent =
    formatDuration(
        data.net_today_seconds || 0
    );

document.getElementById(
    "netWeekTotal"
).textContent =
    formatDuration(
        data.net_week_seconds || 0
    );

document.getElementById(
    "netMonthTotal"
).textContent =
    formatDuration(
        data.net_month_seconds || 0
    );

} catch (error) {

    console.error(error);
}


}
async function refreshDashboard() {

    await loadStatus();

    await loadBreakStatus();

    await updateTotals();

    await loadHistory();

}
document
.getElementById(
"refreshButton"
)
.addEventListener(
"click",
refreshDashboard
);

document
.getElementById(
"startBreakButton"
)
.addEventListener(
"click",
startBreak
);

document
.getElementById(
"endBreakButton"
)
.addEventListener(
"click",
endBreak
);

refreshDashboard();

setInterval(
tickTimer,
1000
);

setInterval(
refreshDashboard,
10000
);

