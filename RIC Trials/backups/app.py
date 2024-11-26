from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/cell_load', methods=['POST'])
def cell_load():
    data = request.json
    cell_id = data.get("cell_id")
    load = data.get("load")
    print(f"Received load update for {cell_id}: {load}")
    return jsonify({"status": "load_updated"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
