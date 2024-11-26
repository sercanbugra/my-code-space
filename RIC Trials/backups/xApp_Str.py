from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Threshold for traffic steering
CELL_LOAD_THRESHOLD = 70  # Load threshold for congestion

# Simulated RAN cell load data (Initially empty, will be updated dynamically)
cell_loads = {
    "cell_1": 0,  # Initially no load
    "cell_2": 0,  # Initially no load
    "cell_3": 0   # Initially no load
}

@app.route('/update_threshold', methods=['POST'])
def update_threshold():
    global CELL_LOAD_THRESHOLD
    data = request.get_json()

    # Ensure the threshold is between 50 and 99
    threshold = data.get('threshold')
    if threshold is not None:
        if 50 <= threshold <= 99:
            CELL_LOAD_THRESHOLD = threshold
            print(f"Updated threshold to: {CELL_LOAD_THRESHOLD}")
            return jsonify({"status": "success", "message": f"Threshold updated to {CELL_LOAD_THRESHOLD}"}), 200
        else:
            return jsonify({"status": "error", "message": "Threshold must be between 50 and 99"}), 400
    else:
        return jsonify({"status": "error", "message": "Threshold value is required"}), 400

# Endpoint for health check
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "running"}), 200

# Endpoint to receive cell load data from the simulator
@app.route('/cell_load', methods=['POST'])
def update_cell_load():
    try:
        data = request.get_json()  # This should be a list of dicts

        if not isinstance(data, list):
            return jsonify({"status": "error", "message": "Expected a list of cell load data"}), 400

        for cell in data:
            cell_id = cell.get('cell_id')
            load = cell.get('load', 0)
            if cell_id not in cell_loads:
                return jsonify({"status": "error", "message": f"Unknown cell {cell_id}"}), 400

            cell_loads[cell_id] = load
            print(f"Cell {cell_id} load: {load}")

        return jsonify({"status": "success", "message": "Cell load updated successfully"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Endpoint for traffic steering decision
@app.route('/traffic_steering', methods=['POST'])
def traffic_steering():
    data = request.json
    ue_id = data.get("ue_id")
    serving_cell = data.get("serving_cell")

    if not ue_id or not serving_cell:
        return jsonify({"error": "Invalid data format. 'ue_id' and 'serving_cell' are required"}), 400

    # Check if the serving cell is congested
    current_load = cell_loads.get(serving_cell, 0)
    if current_load >= CELL_LOAD_THRESHOLD:
        # Find alternative cell with lower load
        target_cell = None
        for cell_id, load in cell_loads.items():
            if load < CELL_LOAD_THRESHOLD and cell_id != serving_cell:
                target_cell = cell_id
                break

        # Prepare traffic steering recommendation
        if target_cell:
            response = {
                "ue_id": ue_id,
                "action": "steer",
                "from_cell": serving_cell,
                "to_cell": target_cell,
                "reason": f"{serving_cell} is congested ({current_load} UEs)"
            }
            # Optionally update cell load after steering decision
            cell_loads[serving_cell] -= 1  # Assuming one user leaves the serving cell
            cell_loads[target_cell] += 1  # Assuming one user is redirected to the target cell
        else:
            response = {
                "ue_id": ue_id,
                "action": "no_steering",
                "reason": "No alternative cell available with lower load"
            }
    else:
        response = {
            "ue_id": ue_id,
            "action": "no_steering",
            "reason": f"{serving_cell} load is acceptable ({current_load} UEs)"
        }

    return jsonify(response), 200

# Endpoint to get current cell load (new method for retrieving cell load)
@app.route('/cell_load', methods=['GET'])
def get_cell_load():
    return jsonify({"cell_loads": cell_loads}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
