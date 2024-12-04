// Arrays to hold UEs in each cell
let cell_1_ues = [];
let cell_2_ues = [];
let cell_3_ues = [];
let cell_12_ues = [];
let cell_22_ues = [];
let cell_32_ues = [];

// Object to track cell loads
let cell_loads = {
    cell_1: 0,
    cell_2: 0,
    cell_3: 0,
    cell_12: 0,
    cell_22: 0,
    cell_32: 0
};

// Constants for UE generation and lifespan
const UE_GENERATION_INTERVAL = 1000; // Generate UE every second
const UE_LIFESPAN = 10000;           // Each UE lasts 10 seconds
const STEERING_THRESHOLD = 10;       // Threshold for traffic steering
const MAX_HISTORY_POINTS = 20;       // Limit for sliding window chart
let steeringMarkers = [];            // Store steering events

    // Define site limits
const SITE_LIMIT = 20; // Maximum total UEs per site
const PRIMARY_LIMIT = 15;
const SECONDARY_LIMIT = 5;

// Cell load history for the chart
const cellLoadHistory = {
    cell_1: [],
    cell_2: [],
    cell_3: [],
    cell_12: [],
    cell_22: [],
    cell_32: []
};

// Initialize the chart
const ctx = document.getElementById('ueCountChart').getContext('2d');
const ueCountChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [
            { label: 'Cell 1', data: cellLoadHistory.cell_1, borderColor: 'red', fill: false },
            { label: 'Cell 2', data: cellLoadHistory.cell_2, borderColor: 'blue', fill: false },
            { label: 'Cell 3', data: cellLoadHistory.cell_3, borderColor: 'green', fill: false },
            { label: 'Cell 12', data: cellLoadHistory.cell_12, borderColor: 'orange', fill: false },
            { label: 'Cell 22', data: cellLoadHistory.cell_22, borderColor: 'purple', fill: false },
            { label: 'Cell 32', data: cellLoadHistory.cell_32, borderColor: 'brown', fill: false }
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
    cellLoadHistory.cell_12.push(cell_loads.cell_12);
    cellLoadHistory.cell_22.push(cell_loads.cell_22);
    cellLoadHistory.cell_32.push(cell_loads.cell_32);

    ueCountChart.data.labels.push(timeLabel);

    if (ueCountChart.data.labels.length > MAX_HISTORY_POINTS) {
        ueCountChart.data.labels.shift();
        Object.keys(cellLoadHistory).forEach(key => cellLoadHistory[key].shift());
    }

    ueCountChart.data.datasets.forEach((dataset, i) => {
        dataset.data = cellLoadHistory[Object.keys(cellLoadHistory)[i]];
    });

    ueCountChart.update();
}

// Throttle chart updates
let chartUpdateTimeout;
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
        const cellId = `cell_${Math.floor(Math.random() * 6) + 1}`;
        ueData.push({ id: ueId, cell: cellId });

        const cellArray = {
            cell_1: cell_1_ues,
            cell_2: cell_2_ues,
            cell_3: cell_3_ues,
            cell_12: cell_12_ues,
            cell_22: cell_22_ues,
            cell_32: cell_32_ues
        }[cellId];

        cellArray.push(ueId);
        generateUEDot(cellId, ueId);
    }

    updateCellCounts();
    setTimeout(removeUE, UE_LIFESPAN, ueData);
}

// Generate UE dot
function generateUEDot(cellId, ueId) {
    const radius = 50;
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
        const cellArray = {
            cell_1: cell_1_ues,
            cell_2: cell_2_ues,
            cell_3: cell_3_ues,
            cell_12: cell_12_ues,
            cell_22: cell_22_ues,
            cell_32: cell_32_ues
        }[ue.cell];
        const index = cellArray.indexOf(ue.id);
        if (index > -1) cellArray.splice(index, 1);
    });
    updateCellCounts();
}

// Update cell counts
function updateCellCounts() {
    Object.keys(cell_loads).forEach(key => {
        cell_loads[key] = {
            cell_1: cell_1_ues.length,
            cell_2: cell_2_ues.length,
            cell_3: cell_3_ues.length,
            cell_12: cell_12_ues.length,
            cell_22: cell_22_ues.length,
            cell_32: cell_32_ues.length
        }[key];
    });

    document.getElementById("count-cell-1").innerText = cell_loads.cell_1;
    document.getElementById("count-cell-2").innerText = cell_loads.cell_2;
    document.getElementById("count-cell-3").innerText = cell_loads.cell_3;
    document.getElementById("count-cell-12").innerText = cell_loads.cell_12;
    document.getElementById("count-cell-22").innerText = cell_loads.cell_22;
    document.getElementById("count-cell-32").innerText = cell_loads.cell_32;

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
    // Define the cell correlations
    const cellCorrelation = {
        cell_1: "cell_12",
        cell_12: "cell_1",
        cell_2: "cell_22",
        cell_22: "cell_2",
        cell_3: "cell_32",
        cell_32: "cell_3"
    };



    // Define site mappings
    const sites = {
        SiteA: ["cell_1", "cell_12"],
        SiteB: ["cell_2", "cell_22"],
        SiteC: ["cell_3", "cell_32"]
    };

    Object.keys(cell_loads).forEach(cellId => {
        // Determine site and target cell
        const targetCell = cellCorrelation[cellId];
        const site = Object.entries(sites).find(([_, cells]) => cells.includes(cellId))[0];

        // Calculate total site load
        const siteLoad = sites[site].reduce((total, cell) => total + cell_loads[cell], 0);

        if (
            cell_loads[cellId] > STEERING_THRESHOLD && 
            siteLoad < SITE_LIMIT && 
            targetCell && 
            cell_loads[targetCell] < (targetCell.endsWith("2") ? SECONDARY_LIMIT : PRIMARY_LIMIT)
        ) {
            // Find and move a UE from the source cell to the target cell
            const sourceArray = {
                cell_1: cell_1_ues,
                cell_2: cell_2_ues,
                cell_3: cell_3_ues,
                cell_12: cell_12_ues,
                cell_22: cell_22_ues,
                cell_32: cell_32_ues
            }[cellId];

            const targetArray = {
                cell_1: cell_1_ues,
                cell_2: cell_2_ues,
                cell_3: cell_3_ues,
                cell_12: cell_12_ues,
                cell_22: cell_22_ues,
                cell_32: cell_32_ues
            }[targetCell];

            if (sourceArray.length > 0) {
                const movedUE = sourceArray.pop(); // Remove UE from source cell
                targetArray.push(movedUE);         // Add UE to target cell

                // Update cell loads
                cell_loads[cellId]--;
                cell_loads[targetCell]++;

                // Log the steering event
                const timeLabel = new Date().toLocaleTimeString();
                updateConsole(`Steering UE (${movedUE}) from ${cellId} to ${targetCell}`);
                steeringMarkers.push({
                    type: 'point',
                    xValue: timeLabel,
                    yValue: cell_loads[cellId],
                    backgroundColor: 'orange',
                    radius: 5,
                    label: { content: `${cellId}→${targetCell}`, enabled: true }
                });
                ueCountChart.update();
            }
        } else if (siteLoad >= SITE_LIMIT) {
            // Log if the site is at capacity
            updateConsole(`Site ${site} is at capacity (${siteLoad} UEs). No additional UEs can be assigned.`);
        }
    });
}


// Start generating UEs
setInterval(generateUE, UE_GENERATION_INTERVAL);
