from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Mengizinkan akses CORS
socketio = SocketIO(app, cors_allowed_origins="*")  # Aktifkan Socket.IO

# Simpan data dalam struktur sederhana (simulasi database)
data_sensors = {}

@app.route('/api/sensor', methods=['POST'])
def save_sensor_data():
    """
    Endpoint untuk menerima data dari ESP32 dan mengirimkan data real-time ke klien.
    """
    try:
        data = request.json
        id_domba = data.get('id_domba')
        berat = data.get('berat')
        suhu = data.get('suhu')
        tinggi = data.get('tinggi')

        if not id_domba or berat is None or suhu is None or tinggi is None:
            return jsonify({"error": "Data tidak lengkap"}), 400

        # Simpan data sensor
        if id_domba not in data_sensors:
            data_sensors[id_domba] = []
        data_sensors[id_domba].append({"berat": berat, "suhu": suhu, "tinggi": tinggi})

        # Kirim data ke klien melalui Socket.IO
        socketio.emit('sensor_update', {"berat": berat, "suhu": suhu, "tinggi": tinggi})

        return jsonify({"message": "Data berhasil disimpan"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """
    Fungsi yang dipanggil saat klien terhubung.
    """
    print("Klien terhubung ke server.")

@socketio.on('disconnect')
def handle_disconnect():
    """
    Fungsi yang dipanggil saat klien terputus.
    """
    print("Klien terputus dari server.")

if __name__ == '__main__':
    # Gunakan socketio.run() untuk menjalankan server
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
