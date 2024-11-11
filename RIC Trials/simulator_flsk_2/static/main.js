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

// Store the last 20 data points for the sliding window effect
const cellLoadHistory = {
    cell_1: [],
    cell_2: [],
    cell_3: []
};

// Array to store steering events to mark on the chart
let steeringMarkers = [];

// Initialize the chart
const ctx = document.getElementById('ueCountChart').getContext('2d');
const ueCountChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [], // Time labels, will be updated dynamically
        datasets: [
            {
                label: 'Cell 1',
                data: cellLoadHistory.cell_1,
                borderColor: 'red',
                fill: false
            },
            {
                label: 'Cell 2',
                data: cellLoadHistory.cell_2,
                borderColor: 'blue',
                fill: false
            },
            {
                label: 'Cell 3',
                data: cellLoadHistory.cell_3,
                borderColor: 'green',
                fill: false
            }
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
            annotation: {
                annotations: steeringMarkers // Add markers to the chart
            }
        }
    }
});

// Function to update the chart with real-time data
function updateChart() {
    const timeLabel = new Date().toLocaleTimeString();

    // Add the current UE count to the history
    cellLoadHistory.cell_1.push(cell_loads.cell_1);
    cellLoadHistory.cell_2.push(cell_loads.cell_2);
    cellLoadHistory.cell_3.push(cell_loads.cell_3);

    // Add the time label and remove older data if we exceed 20 points
    ueCountChart.data.labels.push(timeLabel);
    if (ueCountChart.data.labels.length > 20) {
        ueCountChart.data.labels.shift();
        cellLoadHistory.cell_1.shift();
        cellLoadHistory.cell_2.shift();
        cellLoadHistory.cell_3.shift();
    }

    // Update the chart datasets
    ueCountChart.data.datasets[0].data = cellLoadHistory.cell_1;
    ueCountChart.data.datasets[1].data = cellLoadHistory.cell_2;
    ueCountChart.data.datasets[2].data = cellLoadHistory.cell_3;

    // Refresh the chart
    ueCountChart.update();
}

// Function to generate UEs and update counts
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

        // Generate dot for UE
        generateUEDot(cellId, ueId);
    }

    updateCellCounts();
    setTimeout(removeUE, UE_LIFESPAN, ueData);
}

// Function to generate UE dot inside a cell's circular area
function generateUEDot(cellId, ueId) {
    const radius = 30; // The radius of the cell area where the dot will appear
    const angle = Math.random() * 2 * Math.PI; // Random angle for position
    const distance = Math.sqrt(Math.random()) * radius; // Random distance to spread dots within the circle
    const x = Math.cos(angle) * distance;
    const y = Math.sin(angle) * distance;

    // Create a dot for the UE
    const dot = document.createElement("div");
    dot.classList.add("ue-dot");
    dot.style.left = `calc(50% + ${x}% )`; // Position the dot based on the calculated position
    dot.style.top = `calc(50% + ${y}% )`; // Position the dot based on the calculated position
    dot.setAttribute("data-ue-id", ueId);
    document.getElementById(cellId).appendChild(dot);

    // Track dots by UE ID
    setTimeout(() => removeUEDot(ueId, dot, cellId), UE_LIFESPAN);
}

// Function to remove UE dot from the cell
function removeUEDot(ueId, dot, cellId) {
    const cell = document.getElementById(cellId);
    if (cell && dot) {
        cell.removeChild(dot);
    }
}

// Function to remove UEs
function removeUE(ueData) {
    ueData.forEach(ue => {
        if (ue.cell === "cell_1") {
            const index = cell_1_ues.indexOf(ue.id);
            if (index > -1) cell_1_ues.splice(index, 1);
        } else if (ue.cell === "cell_2") {
            const index = cell_2_ues.indexOf(ue.id);
            if (index > -1) cell_2_ues.splice(index, 1);
        } else if (ue.cell === "cell_3") {
            const index = cell_3_ues.indexOf(ue.id);
            if (index > -1) cell_3_ues.splice(index, 1);
        }
    });
    updateCellCounts();
}

// Update cell counts and refresh the chart
function updateCellCounts() {
    cell_loads.cell_1 = cell_1_ues.length;
    cell_loads.cell_2 = cell_2_ues.length;
    cell_loads.cell_3 = cell_3_ues.length;

    document.getElementById("count-cell-1").innerText = cell_loads.cell_1;
    document.getElementById("count-cell-2").innerText = cell_loads.cell_2;
    document.getElementById("count-cell-3").innerText = cell_loads.cell_3;

    const cellLoadData = JSON.stringify({
        "cell_1": cell_loads.cell_1,
        "cell_2": cell_loads.cell_2,
        "cell_3": cell_loads.cell_3
    });
    updateConsole(cellLoadData);

    // Update the chart with the new counts
    updateChart();

    // Check for steering conditions
    checkTrafficSteering();
}

// Console log function
function updateConsole(message) {
    const consoleOutput = document.getElementById("console");
    consoleOutput.innerHTML += message + "\n";
    consoleOutput.scrollTop = consoleOutput.scrollHeight;
}

// Traffic steering logic with steering markers
function checkTrafficSteering() {
    Object.keys(cell_loads).forEach(cellId => {
        if (cell_loads[cellId] > 10) {
            const targetCell = Object.keys(cell_loads).reduce((minCell, cell) => {
                return cell_loads[cell] < cell_loads[minCell] ? cell : minCell;
            }, cellId);

            if (targetCell !== cellId) {
                const ueToMove = {
                    current_cell: cellId,
                    target_cell: targetCell,
                    ue_id: `UE_${Date.now()}` // Test for a unique UE ID
                };

                // Post to xApp and log steering decision
                fetch("http://localhost:5001/traffic_steering", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(ueToMove)
                }).then(response => response.json())
                  .then(data => {
                      const timeLabel = new Date().toLocaleTimeString();
                      const logMessage = `Steering triggered: Moving ${ueToMove.ue_id} from ${cellId} to ${targetCell} at ${timeLabel}`;
                      updateConsole(logMessage);

                      // Add a marker for this steering event on the chart
                      steeringMarkers.push({
                          type: 'point',
                          xValue: timeLabel,
                          yValue: cell_loads[cellId],
                          backgroundColor: 'orange',
                          radius: 5,
                          label: {
                              content: `Steer ${cellId}→${targetCell}`,
                              enabled: true,
                              position: 'center'
                          }
                      });
                      ueCountChart.update();
                  });
            }
        }
    });
}

// Generate UEs periodically
setInterval(generateUE, UE_GENERATION_INTERVAL);
