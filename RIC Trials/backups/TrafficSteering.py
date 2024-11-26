from flask import Flask, request, jsonify

app = Flask(__name__)

# Thresholds for traffic steering
CELL_LOAD_THRESHOLD = 80  # Percentage load threshold for congestion

# Simulated RAN cell load data (in a real xApp, data would come from RIC)
cell_loads = {
    "cell_1": 75,  # Not congested
    "cell_2": 85,  # Congested
    "cell_3": 60   # Not congested
}

# Endpoint for health check
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "running"}), 200

# Endpoint to receive cell load data
@app.route('/cell_load', methods=['POST'])
def update_cell_load():
    data = request.json
    cell_id = data.get("cell_id")
    load = data.get("load")

    if not cell_id or load is None:
        return jsonify({"error": "Invalid data format"}), 400

    # Update cell load
    cell_loads[cell_id] = load
    print(f"Updated load for {cell_id}: {load}%")

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
                "reason": f"{serving_cell} is congested ({current_load}%)"
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
            "reason": f"{serving_cell} load is acceptable ({current_load}%)"
        }

    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
