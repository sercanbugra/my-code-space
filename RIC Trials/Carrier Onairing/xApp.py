from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/traffic_steering', methods=['POST'])
def traffic_steering():
    data = request.get_json()

    # Veriyi kontrol et
    print("Received traffic steering data:", data)

    ue_id = data.get('ue_id')
    current_cell = data.get('current_cell')
    target_cell = data.get('target_cell')

    # Burada, hücreler arasında kaydırma işlemi yapılabilir (örneğin, DB güncellenebilir)
    print(f"Steering UE {ue_id} from {current_cell} to {target_cell}")

    response = {
        'status': 'success',
        'message': f'UE {ue_id} moved from {current_cell} to {target_cell}',
        'current_cell': current_cell,
        'target_cell': target_cell,
        'ue_id': ue_id
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
