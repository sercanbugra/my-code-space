from flask import Flask, request, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
# Thresholds for traffic steering
CELL_LOAD_THRESHOLD = 70  # load threshold for congestion

# Simulated RAN cell load data (Initially empty, will be updated dynamically)
cell_loads = {
    "cell_1": 0,  # Initially no load
    "cell_2": 0,  # Initially no load
    "cell_3": 0   # Initially no load
}

# Endpoint for health check
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "running"}), 200

# Endpoint to receive cell load data from the simulator
@app.route('/cell_load', methods=['POST'])
def update_cell_load():
    data = request.get_json()  # Parse the incoming JSON request
    print(f"Received data: {data}")  # Log the incoming data on the server
    if not data or "cell_id" not in data or "load" not in data:
        return jsonify({"error": "Invalid data format"}), 400

    cell_id = data["cell_id"]
    load = data["load"]
    
    # Update the cell load (in your actual code, this would update a database or in-memory data)
    cell_loads[cell_id] = load
    print(f"Updated load for {cell_id}: {load} UEs")

    return jsonify({"status": "load updated", "cell_loads": cell_loads}), 200


# Endpoint for traffic steering decision
@app.route('/traffic_steering', methods=['POST'])
def traffic_steering():
    data = request.json
    ue_id = data.get("ue_id")
    serving_cell = data.get("serving_cell")

    if not ue_id or not serving_cell:
        return jsonify({"error": "Invalid data format"}), 400

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

# Endpoint to get current cell load
@app.route('/cell_load', methods=['GET'])
def get_cell_load():
    return jsonify({"cell_loads": cell_loads}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
