from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Threshold for traffic steering
CELL_LOAD_THRESHOLD = 70  # Default load threshold for congestion

# Global variable to store the last steering decision
last_steering_decision = {}

# Cell loads initialization
cell_loads = {
    "cell_1": 0,
    "cell_2": 0,
    "cell_3": 0
}

# Serve the main page
@app.route('/')
def index():
    return render_template('index.html')

# Endpoint to update the load threshold
@app.route('/update_threshold', methods=['POST'])
def update_threshold():
    global CELL_LOAD_THRESHOLD
    data = request.get_json()
    threshold = data.get('threshold')
    if 50 <= threshold <= 99:
        CELL_LOAD_THRESHOLD = threshold
        return jsonify({"status": "success", "message": f"Threshold updated to {CELL_LOAD_THRESHOLD}"}), 200
    else:
        return jsonify({"status": "error", "message": "Threshold must be between 50 and 99"}), 400

# Endpoint to update cell load
@app.route('/cell_load', methods=['POST'])
def update_cell_load():
    try:
        # Get data from the request body (this is a list of cells)
        data = request.get_json()

        # Iterate through the list and process each cell
        for cell in data:
            cell_id = cell["cell_id"]
            load = cell["load"]
            # Process cell data here (e.g., update your database or logic)
            print(f"Updating cell {cell_id} with load {load}")

        # Return a response
        return jsonify({"status": "success", "message": "Cell load updated successfully"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Endpoint to decide traffic steering
@app.route('/traffic_steering', methods=['POST'])
def traffic_steering():
    global last_steering_decision
    data = request.json
    ue_id = data.get("ue_id")
    serving_cell = data.get("serving_cell")
    current_load = cell_loads.get(serving_cell, 0)

    # Check for congestion
    if current_load >= CELL_LOAD_THRESHOLD:
        # Find the cell with the lowest load
        target_cell = min(cell_loads, key=cell_loads.get)
        if target_cell != serving_cell:
            last_steering_decision = {
                "ue_id": ue_id,
                "from_cell": serving_cell,
                "to_cell": target_cell
            }
            response = {"status": "steer", **last_steering_decision}
        else:
            response = {"status": "no_steering", "reason": "No alternative cell available"}
    else:
        response = {"status": "no_steering", "reason": f"{serving_cell} load is acceptable"}
    
    return jsonify(response), 200

# Endpoint to retrieve the last steering decision
@app.route('/get_steering_decision', methods=['GET'])
def get_steering_decision():
    global last_steering_decision
    if last_steering_decision:
        decision = last_steering_decision
        last_steering_decision = {}  # Clear after sending
        return jsonify(decision), 200
    else:
        return jsonify({"status": "no_decision"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
