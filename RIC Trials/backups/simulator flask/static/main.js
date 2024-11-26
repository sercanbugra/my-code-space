// Function to update threshold on the backend
function updateThreshold() {
    const threshold = parseInt(document.getElementById("threshold").value);
    
    // Check if threshold is a valid number
    if (isNaN(threshold) || threshold < 50 || threshold > 99) {
        alert("Please enter a valid threshold between 50 and 99.");
        return;
    }

    // Send the updated threshold to the backend
    fetch('/update_threshold', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ threshold: threshold })
    })
    .then(response => response.json())
    .then(data => alert(data.message)) // Show success message to the user
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to update threshold.');
    });
}

// Function to send cell load data to the backend
function updateCellLoad(cell_id, load) {
    // Prepare cell load data as an array of objects
    const cellData = [{ cell_id: cell_id, load: load }];
    
    // Send the updated cell load data to the backend
    fetch('http://localhost:5001/cell_load', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(cellData)
    })
    .then(response => response.json())
    .then(data => {
        // If data returns success, update the console on the browser
        updateConsole(`Cell load update successful: ${data.message}`);
    })
    .catch(error => {
        updateConsole(`Error: ${error}`);
    });
}

// Function to update the console on the page with messages
function updateConsole(message) {
    console.log(message);  // This will log to the browser's console
    // Update the console div with the new message
    document.getElementById("console").innerText += message + '\n';
}

// Sample periodic cell load update simulation
setInterval(() => {
    const cell1Load = Math.floor(Math.random() * 100);
    const cell2Load = Math.floor(Math.random() * 100);
    const cell3Load = Math.floor(Math.random() * 100);
    
    // Update cell load for each cell
    updateCellLoad("cell_1", cell1Load);
    updateCellLoad("cell_2", cell2Load);
    updateCellLoad("cell_3", cell3Load);
    
}, 5000);

