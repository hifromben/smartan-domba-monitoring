from flask import Flask, request, jsonify, send_from_directory, abort
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# File JSON untuk menyimpan data vaksin
DATA_FILE = "vaccine_data.json"

# Fungsi untuk memuat data vaksin dari file JSON
def load_vaccine_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return {}

# Fungsi untuk menyimpan data vaksin ke file JSON
def save_vaccine_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Memuat data vaksin saat server pertama kali berjalan
data_vaksin = load_vaccine_data()

# Menyimpan data sensor dalam memori sementara
data_sensors = {}

# ==============================================
# ✅ **Endpoint untuk menyimpan data sensor**
# ==============================================
@app.route('/api/sensor', methods=['POST'])
def save_sensor_data():
    try:
        data = request.json
        print("✅ Data sensor diterima:", data)

        id_domba = data.get('id_domba')
        berat = data.get('berat')
        suhu = data.get('suhu')
        tinggi = data.get('tinggi')

        if not id_domba or berat is None or suhu is None or tinggi is None:
            return jsonify({"error": "⚠️ Data tidak lengkap"}), 400

        if id_domba not in data_sensors:
            data_sensors[id_domba] = []

        data_sensors[id_domba].append({
            "berat": berat,
            "suhu": suhu,
            "tinggi": tinggi
        })

        # Emit data terbaru ke client melalui Socket.IO (Real-time update)
        sensor_data = {"berat": berat, "suhu": suhu, "tinggi": tinggi}
        socketio.emit('sensor_update', sensor_data)

        return jsonify({"message": "✅ Data berhasil disimpan"}), 201
    except Exception as e:
        print("❌ Error saat menyimpan data sensor:", str(e))
        return jsonify({"error": str(e)}), 500

# =================================================
# ✅ **Endpoint untuk mengambil data sensor**
# =================================================
@app.route('/api/sensor/<id_domba>', methods=['GET'])
def get_sensor_data(id_domba):
    if id_domba not in data_sensors:
        return jsonify({"error": "❌ Data tidak ditemukan untuk ID domba ini"}), 404

    return jsonify({
        "id_domba": id_domba,
        "data": data_sensors[id_domba]
    }), 200

# =================================================
# ✅ **Endpoint untuk menyimpan data vaksin**
# =================================================
@app.route('/api/vaccine', methods=['POST'])
def save_vaccine_data_api():
    try:
        data = request.json
        id_domba = data.get('id_domba')
        jenis_vaksin = data.get('jenis_vaksin')
        tanggal = data.get('tanggal')

        if not id_domba or not jenis_vaksin or not tanggal:
            return jsonify({"error": "⚠️ Data tidak lengkap"}), 400

        if id_domba not in data_vaksin:
            data_vaksin[id_domba] = []

        data_vaksin[id_domba].append({
            "jenis_vaksin": jenis_vaksin,
            "tanggal": tanggal
        })

        # Simpan data ke file JSON agar tidak hilang setelah restart
        save_vaccine_data(data_vaksin)

        return jsonify({
            "message": "✅ Data vaksin berhasil disimpan",
            "riwayat_vaksin": data_vaksin[id_domba]
        }), 201
    except Exception as e:
        print("❌ Error saat menyimpan data vaksin:", str(e))
        return jsonify({"error": f"Terjadi kesalahan: {str(e)}"}), 500

# =================================================
# ✅ **Endpoint untuk mengambil riwayat vaksin**
# =================================================
@app.route('/api/vaccine/<id_domba>', methods=['GET'])
def get_vaccine_data(id_domba):
    if id_domba not in data_vaksin:
        return jsonify({"error": "❌ Data vaksin tidak ditemukan"}), 404

    return jsonify({
        "id_domba": id_domba,
        "riwayat_vaksin": data_vaksin[id_domba]
    }), 200

# ==========================================================
# ✅ **Endpoint untuk menghapus data vaksin berdasarkan index**
# ==========================================================
@app.route('/api/vaccine/<id_domba>/<int:index>', methods=['DELETE'])
def delete_vaccine_data(id_domba, index):
    try:
        if id_domba in data_vaksin and 0 <= index < len(data_vaksin[id_domba]):
            removed_item = data_vaksin[id_domba].pop(index)
            save_vaccine_data(data_vaksin)  # Simpan perubahan ke file JSON
            return jsonify({"message": "✅ Data vaksin berhasil dihapus", "data": removed_item}), 200

        return jsonify({"error": "❌ Data tidak ditemukan"}), 404
    except Exception as e:
        print("❌ Error saat menghapus data vaksin:", str(e))
        return jsonify({"error": f"Terjadi kesalahan: {str(e)}"}), 500

# ==========================================================
# ✅ **Socket.IO handler untuk koneksi real-time**
# ==========================================================
@socketio.on('connect')
def handle_connect():
    print("📡 Client terhubung")

@socketio.on('disconnect')
def handle_disconnect():
    print("🔌 Client terputus")

# ==========================================================
# ✅ **Endpoint untuk mengakses halaman utama `index.html`**
# ==========================================================
@app.route('/')
def serve_index():
    try:
        return send_from_directory('.', 'index.html')
    except FileNotFoundError:
        print("❌ Error: File `index.html` tidak ditemukan.")
        abort(404)

# ==========================================================
# ✅ **Endpoint untuk melayani file statis (HTML, CSS, JS)**
# ==========================================================
@app.route('/<path:filename>')
def serve_static_file(filename):
    if os.path.isfile(filename):
        return send_from_directory('.', filename)
    else:
        print(f"❌ Error: File `{filename}` tidak ditemukan.")
        abort(404)

# ==========================================================
# ✅ **Menjalankan aplikasi Flask**
# ==========================================================
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
