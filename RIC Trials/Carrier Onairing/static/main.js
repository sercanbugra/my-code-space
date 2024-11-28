let cell_1_ues = [];
let cell_2_ues = [];
let cell_3_ues = [];
let cell_loads = {
    cell_1: 0,
    cell_2: 0,
    cell_3: 0
};

const UE_GENERATION_INTERVAL = 1000; // Generate UE every second
const UE_LIFESPAN = 10000;           // Each UE lasts 10 seconds
const STEERING_THRESHOLD = 10;       // Threshold for traffic steering
const MAX_HISTORY_POINTS = 20;       // Limit for sliding window chart
let steeringMarkers = [];            // Store steering events

const cellLoadHistory = {
    cell_1: [],
    cell_2: [],
    cell_3: []
};

let chartUpdateTimeout; // For throttling chart updates

// Initialize the chart
const ctx = document.getElementById('ueCountChart').getContext('2d');
const ueCountChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [
            { label: 'Cell 1', data: cellLoadHistory.cell_1, borderColor: 'red', fill: false },
            { label: 'Cell 2', data: cellLoadHistory.cell_2, borderColor: 'blue', fill: false },
            { label: 'Cell 3', data: cellLoadHistory.cell_3, borderColor: 'green', fill: false }
        ]
    },
    options: {
        responsive: true,
        animation: false,
        scales: {
            x: { title: { display: true, text: 'Time' } },
            y: { beginAtZero: true, title: { display: true, text: 'UE Count' } }
        },
        plugins: {
            annotation: { annotations: steeringMarkers }
        }
    }
});

// Function to update the chart
function updateChart() {
    const timeLabel = new Date().toLocaleTimeString();

    cellLoadHistory.cell_1.push(cell_loads.cell_1);
    cellLoadHistory.cell_2.push(cell_loads.cell_2);
    cellLoadHistory.cell_3.push(cell_loads.cell_3);

    ueCountChart.data.labels.push(timeLabel);

    if (ueCountChart.data.labels.length > MAX_HISTORY_POINTS) {
        ueCountChart.data.labels.shift();
        cellLoadHistory.cell_1.shift();
        cellLoadHistory.cell_2.shift();
        cellLoadHistory.cell_3.shift();
    }

    ueCountChart.data.datasets[0].data = cellLoadHistory.cell_1;
    ueCountChart.data.datasets[1].data = cellLoadHistory.cell_2;
    ueCountChart.data.datasets[2].data = cellLoadHistory.cell_3;

    ueCountChart.update();
}

// Throttle chart updates
function throttleChartUpdate() {
    if (chartUpdateTimeout) return;
    chartUpdateTimeout = setTimeout(() => {
        updateChart();
        chartUpdateTimeout = null;
    }, 500);
}

// Generate UEs
function generateUE() {
    const ueCount = Math.floor(Math.random() * 5) + 1;
    const ueData = [];

    for (let i = 0; i < ueCount; i++) {
        const ueId = `UE_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
        const cellId = `cell_${Math.floor(Math.random() * 3) + 1}`;
        ueData.push({ id: ueId, cell: cellId });

        if (cellId === "cell_1") cell_1_ues.push(ueId);
        else if (cellId === "cell_2") cell_2_ues.push(ueId);
        else if (cellId === "cell_3") cell_3_ues.push(ueId);

        generateUEDot(cellId, ueId);
    }

    updateCellCounts();
    setTimeout(removeUE, UE_LIFESPAN, ueData);
}

// Generate UE dot
function generateUEDot(cellId, ueId) {
    const radius = 30;
    const angle = Math.random() * 2 * Math.PI;
    const distance = Math.sqrt(Math.random()) * radius;
    const x = Math.cos(angle) * distance;
    const y = Math.sin(angle) * distance;

    const dot = document.createElement("div");
    dot.classList.add("ue-dot");
    dot.style.left = `calc(50% + ${x}px)`;
    dot.style.top = `calc(50% + ${y}px)`;
    dot.setAttribute("data-ue-id", ueId);
    document.getElementById(cellId).appendChild(dot);

    setTimeout(() => removeUEDot(dot, cellId), UE_LIFESPAN);
}

// Remove UE dot
function removeUEDot(dot, cellId) {
    const cell = document.getElementById(cellId);
    if (cell && dot && dot.parentNode === cell) {
        cell.removeChild(dot);
    }
}

// Remove UEs
function removeUE(ueData) {
    ueData.forEach(ue => {
        const index = {
            cell_1: cell_1_ues.indexOf(ue.id),
            cell_2: cell_2_ues.indexOf(ue.id),
            cell_3: cell_3_ues.indexOf(ue.id)
        }[ue.cell];

        if (index > -1) {
            ({
                cell_1: () => cell_1_ues.splice(index, 1),
                cell_2: () => cell_2_ues.splice(index, 1),
                cell_3: () => cell_3_ues.splice(index, 1)
            }[ue.cell])();
        }
    });
    updateCellCounts();
}

// Update cell counts
function updateCellCounts() {
    cell_loads.cell_1 = cell_1_ues.length;
    cell_loads.cell_2 = cell_2_ues.length;
    cell_loads.cell_3 = cell_3_ues.length;

    document.getElementById("count-cell-1").innerText = cell_loads.cell_1;
    document.getElementById("count-cell-2").innerText = cell_loads.cell_2;
    document.getElementById("count-cell-3").innerText = cell_loads.cell_3;

    updateConsole(JSON.stringify(cell_loads));
    throttleChartUpdate();
    checkTrafficSteering();
}

// Update console
function updateConsole(message) {
    const consoleOutput = document.getElementById("console");
    consoleOutput.innerHTML += message + "\n";
    consoleOutput.scrollTop = consoleOutput.scrollHeight;
}

// Traffic steering
function checkTrafficSteering() {
    Object.keys(cell_loads).forEach(cellId => {
        if (cell_loads[cellId] > STEERING_THRESHOLD) {
            const targetCell = Object.keys(cell_loads).reduce((minCell, cell) => {
                return cell_loads[cell] < cell_loads[minCell] ? cell : minCell;
            }, cellId);

            if (targetCell !== cellId) {
                const ueToMove = {
                    current_cell: cellId,
                    target_cell: targetCell,
                    ue_id: `UE_${Date.now()}`
                };

                fetch("http://localhost:5001/traffic_steering", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(ueToMove)
                })
                .then(response => response.json())
                .then(() => {
                    const timeLabel = new Date().toLocaleTimeString();
                    updateConsole(`Steering triggered: ${cellId} → ${targetCell}`);
                    steeringMarkers.push({
                        type: 'point',
                        xValue: timeLabel,
                        yValue: cell_loads[cellId],
                        backgroundColor: 'orange',
                        radius: 5,
                        label: { content: `${cellId}→${targetCell}`, enabled: true }
                    });
                    ueCountChart.update();
                })
                .catch(error => {
                    console.error("Traffic Steering Error:", error);
                    updateConsole("Error: " + error.message);
                });
            }
        }
    });
}

// Periodic UE generation
setInterval(generateUE, UE_GENERATION_INTERVAL);
