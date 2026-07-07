let flowChart;
let saltChart;

let labels = [];

let flowData = [];
let pressureData = [];

let saltData = [];
let tdsData = [];

// ---- Gauge arc circumference (r=50 => 2 * PI * 50) ----
const GAUGE_CIRCUMFERENCE = 314.159;

// ---- Sensor scale maximums used only for gauge fill % (visual only) ----
const GAUGE_SCALE = {
    flow: 30,
    pressure: 5,
    salt: 100,
    tds: 500
};

function updateArc(elementId, percent) {

    const el = document.getElementById(elementId);

    if (!el) return;

    const clamped = Math.max(0, Math.min(100, percent));

    const offset = GAUGE_CIRCUMFERENCE - (clamped / 100) * GAUGE_CIRCUMFERENCE;

    el.style.strokeDashoffset = offset;

}

function colorForHealth(value) {

    if (value >= 80) return getCssVar("--accent-green");
    if (value >= 50) return getCssVar("--accent-amber");
    return getCssVar("--accent-red");

}

function getCssVar(name) {

    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();

}

function showToast(message, type) {

    const host = document.getElementById("toastHost");

    if (!host) {
        // Fallback so functionality is never lost if the host is missing
        alert(message);
        return;
    }

    const toast = document.createElement("div");

    toast.className = "console-toast";

    if (type === "success") toast.style.borderLeftColor = getCssVar("--accent-green");
    else if (type === "warning") toast.style.borderLeftColor = getCssVar("--accent-amber");
    else if (type === "danger") toast.style.borderLeftColor = getCssVar("--accent-red");
    else toast.style.borderLeftColor = getCssVar("--accent-cyan");

    toast.innerText = message;

    host.appendChild(toast);

    setTimeout(() => {

        toast.classList.add("hide");

        setTimeout(() => {
            if (toast.parentNode) toast.parentNode.removeChild(toast);
        }, 300);

    }, 3200);

}

function updateClock() {

    const clockEl = document.getElementById("liveClock");

    if (clockEl) {
        clockEl.innerText = new Date().toLocaleTimeString();
    }

}

function setConnectionStatus(isOnline) {

    const dot = document.getElementById("connDot");
    const label = document.getElementById("connLabel");

    if (!dot || !label) return;

    dot.classList.remove("online", "offline");

    if (isOnline) {

        dot.classList.add("online");
        label.innerText = "ONLINE";

    } else {

        dot.classList.add("offline");
        label.innerText = "OFFLINE";

    }

}

function initializeCharts() {

    const flowCtx = document.getElementById("flowChart").getContext("2d");

    flowChart = new Chart(flowCtx, {

        type: "line",

        data: {

            labels: labels,

            datasets: [

                {
                    label: "Flow (L/min)",
                    data: flowData,
                    borderColor: "#3b82f6",
                    backgroundColor: "rgba(59,130,246,0.12)",
                    fill: true,
                    tension: 0.35,
                    pointRadius: 0,
                    borderWidth: 2
                },

                {
                    label: "Pressure (bar)",
                    data: pressureData,
                    borderColor: "#22d3ee",
                    backgroundColor: "rgba(34,211,238,0.10)",
                    fill: true,
                    tension: 0.35,
                    pointRadius: 0,
                    borderWidth: 2
                }

            ]

        },

        options: {

            responsive: true,
            animation: false,

            interaction: {
                mode: "index",
                intersect: false
            },

            scales: {

                x: {
                    ticks: { color: "#8ea0bd", maxRotation: 0 },
                    grid: { color: "rgba(255,255,255,0.05)" }
                },

                y: {
                    ticks: { color: "#8ea0bd" },
                    grid: { color: "rgba(255,255,255,0.05)" }
                }

            },

            plugins: {

                legend: {
                    labels: { color: "#e7edf6" }
                }

            }

        }

    });

    const saltCtx = document.getElementById("saltChart").getContext("2d");

    saltChart = new Chart(saltCtx, {

        type: "line",

        data: {

            labels: labels,

            datasets: [

                {
                    label: "Salt (%)",
                    data: saltData,
                    borderColor: "#f5a524",
                    backgroundColor: "rgba(245,165,36,0.10)",
                    fill: true,
                    tension: 0.35,
                    pointRadius: 0,
                    borderWidth: 2
                },

                {
                    label: "TDS (ppm)",
                    data: tdsData,
                    borderColor: "#ef5350",
                    backgroundColor: "rgba(239,83,80,0.08)",
                    fill: true,
                    tension: 0.35,
                    pointRadius: 0,
                    borderWidth: 2
                }

            ]

        },

        options: {

            responsive: true,
            animation: false,

            interaction: {
                mode: "index",
                intersect: false
            },

            scales: {

                x: {
                    ticks: { color: "#8ea0bd", maxRotation: 0 },
                    grid: { color: "rgba(255,255,255,0.05)" }
                },

                y: {
                    ticks: { color: "#8ea0bd" },
                    grid: { color: "rgba(255,255,255,0.05)" }
                }

            },

            plugins: {

                legend: {
                    labels: { color: "#e7edf6" }
                }

            }

        }

    });

}

async function loadStats() {

    try {

        const response = await fetch("/stats");

        const stats = await response.json();

        document.getElementById("totalReadings").innerText =
            stats.total_readings;

        document.getElementById("totalLogs").innerText =
            stats.total_logs;

        document.getElementById("totalRegen").innerText =
            stats.total_regenerations;

        document.getElementById("avgHealth").innerText =
            stats.average_health + "%";

    }

    catch (err) {

        console.log(err);

    }

}

async function loadData() {

    try {

        const response = await fetch("/sensor-data");

        const data = await response.json();

        setConnectionStatus(true);

        document.getElementById("flow").innerText = data.flow;
        document.getElementById("pressure").innerText = data.pressure;
        document.getElementById("salt").innerText = data.salt;
        document.getElementById("tds").innerText = data.tds;

        // ---- Gauge arcs (visual only, does not affect underlying data) ----
        updateArc("flowArc", (data.flow / GAUGE_SCALE.flow) * 100);
        updateArc("pressureArc", (data.pressure / GAUGE_SCALE.pressure) * 100);
        updateArc("saltArc", (data.salt / GAUGE_SCALE.salt) * 100);
        updateArc("tdsArc", (data.tds / GAUGE_SCALE.tds) * 100);

        document.getElementById("power").innerText =
            data.power ? "ON" : "OFF";

        document.getElementById("regen").innerText =
            data.regeneration ? "RUNNING" : "OFF";

        document.getElementById("time").innerText =
            data.timestamp;

        document.getElementById("uptime").innerText =
            data.uptime;

        const state = document.getElementById("state");

        state.innerText = data.state;

        state.className = "badge state-badge";

        if (data.state === "MONITORING")
            state.classList.add("bg-success");

        else if (data.state === "REGENERATION_RUNNING")
            state.classList.add("bg-primary");

        else if (data.state === "REGENERATION_REQUIRED")
            state.classList.add("bg-warning");

        else if (data.state === "FAULT")
            state.classList.add("bg-danger");

        else
            state.classList.add("bg-secondary");

        // ---- Regeneration progress strip (visual only) ----
        const regenTrack = document.getElementById("regenTrack");

        if (regenTrack) {

            regenTrack.classList.toggle("active", !!data.regeneration);

            const fill = document.getElementById("regenTrackFill");

            if (fill) fill.style.width = data.regeneration ? "100%" : "0%";

        }

        const healthBar = document.getElementById("healthBar");

        healthBar.style.width = data.health + "%";

        healthBar.innerText = data.health + "%";

        healthBar.className = "progress-bar";

        if (data.health >= 80)
            healthBar.classList.add("bg-success");

        else if (data.health >= 50)
            healthBar.classList.add("bg-warning");

        else
            healthBar.classList.add("bg-danger");

        // ---- Radial health gauge (visual only) ----
        updateArc("healthArc", data.health);

        const healthArcEl = document.getElementById("healthArc");

        if (healthArcEl) healthArcEl.style.stroke = colorForHealth(data.health);

        // ---- Salt tank + flow indicator (visual only) ----
        const saltTankFill = document.getElementById("saltTankFill");

        if (saltTankFill) saltTankFill.style.height = data.salt + "%";

        const flowIndicator = document.getElementById("flowIndicator");

        if (flowIndicator) flowIndicator.classList.toggle("active", data.flow > 0 && data.power);

        const alerts = document.getElementById("alerts");

        alerts.innerHTML = "";

        if (data.alerts.length === 0) {

            alerts.innerHTML =
                `<li class="list-group-item text-success">No Active Alerts</li>`;

        }

        else {

            data.alerts.forEach(alert => {

                alerts.innerHTML +=
                    `<li class="list-group-item text-danger">${alert}</li>`;

            });

        }

        const logs = document.getElementById("logs");

        logs.innerHTML = "";

        data.logs.forEach(log => {

            logs.innerHTML +=
                `<li class="list-group-item">${log}</li>`;

        });

        labels.push(new Date().toLocaleTimeString());

        flowData.push(data.flow);
        pressureData.push(data.pressure);

        saltData.push(data.salt);
        tdsData.push(data.tds);

        if (labels.length > 20) {

            labels.shift();

            flowData.shift();
            pressureData.shift();

            saltData.shift();
            tdsData.shift();

        }

        flowChart.update();
        saltChart.update();

    }

    catch (err) {

        console.log(err);

        setConnectionStatus(false);

    }

}

async function startRegeneration() {

    const response = await fetch("/start-regeneration", {

        method: "POST"

    });

    const result = await response.json();

    showToast(result.message, "success");

    loadData();
    loadStats();

}

async function togglePower() {

    const response = await fetch("/toggle-power", {

        method: "POST"

    });

    const result = await response.json();

    showToast(result.message, "warning");

    loadData();

}

async function refillSalt() {

    const response = await fetch("/refill-salt", {

        method: "POST"

    });

    const result = await response.json();

    showToast(result.message, "success");

    loadData();

}

async function resetFault() {

    const response = await fetch("/reset-fault", {

        method: "POST"

    });

    const result = await response.json();

    showToast(result.message, "danger");

    loadData();

}

initializeCharts();

updateClock();
setInterval(updateClock, 1000);

loadData();
loadStats();

setInterval(() => {

    loadData();
    loadStats();

}, 2000);
