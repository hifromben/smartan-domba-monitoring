from flask import Flask, request, jsonify, send_from_directory, abort
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db
import os

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# ✅ **Inisialisasi Firebase**
cred = credentials.Certificate("firebase_config.json")  # Ganti dengan path file key JSON
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://smartan-domba-garut-default-rtdb.asia-southeast1.firebasedatabase.app"
})

# =========================================
# ✅ **Endpoint untuk menyimpan data sensor**
# =========================================
@app.route('/api/sensor', methods=['POST'])
def save_sensor_data():
    try:
        data = request.json
        id_domba = data.get('id_domba')

        if not id_domba:
            return jsonify({"error": "⚠️ ID domba tidak ditemukan"}), 400

        ref = db.reference(f"/domba/{id_domba}/sensor")
        ref.set({
            "berat": data.get('berat'),
            "suhu": data.get('suhu'),
            "tinggi": data.get('tinggi')
        })

        # Emit data terbaru ke client melalui Socket.IO (Real-time update)
        socketio.emit('sensor_update', data)

        return jsonify({"message": "✅ Data sensor berhasil disimpan"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =========================================
# ✅ **Endpoint untuk mengambil data sensor**
# =========================================
@app.route('/api/sensor/<id_domba>', methods=['GET'])
def get_sensor_data(id_domba):
    ref = db.reference(f"/domba/{id_domba}/sensor")
    data = ref.get()

    if data:
        return jsonify({"id_domba": id_domba, "data": data}), 200
    return jsonify({"error": "❌ Data tidak ditemukan"}), 404

# =========================================
# ✅ **Endpoint untuk menyimpan data vaksin**
# =========================================
@app.route('/api/vaccine', methods=['POST'])
def save_vaccine_data():
    try:
        data = request.json
        id_domba = data.get('id_domba')

        if not id_domba:
            return jsonify({"error": "⚠️ ID domba tidak ditemukan"}), 400

        ref = db.reference(f"/domba/{id_domba}/riwayat_vaksin")
        ref.push({
            "jenis_vaksin": data.get('jenis_vaksin'),
            "tanggal": data.get('tanggal')
        })

        return jsonify({"message": "✅ Data vaksin berhasil disimpan"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =========================================
# ✅ **Endpoint untuk mengambil riwayat vaksin**
# =========================================
@app.route('/api/vaccine/<id_domba>', methods=['GET'])
def get_vaccine_data(id_domba):
    ref = db.reference(f"/domba/{id_domba}/riwayat_vaksin")
    data = ref.get()

    if data:
        return jsonify({"id_domba": id_domba, "riwayat_vaksin": list(data.values())}), 200
    return jsonify({"error": "❌ Data vaksin tidak ditemukan"}), 404

# =========================================
# ✅ **Endpoint untuk menyimpan identitas domba**
# =========================================
@app.route('/api/identity', methods=['POST'])
def save_identity():
    try:
        data = request.json
        id_domba = data.get('id_domba')

        if not id_domba:
            return jsonify({"error": "⚠️ ID domba tidak ditemukan"}), 400

        ref = db.reference(f"/domba/{id_domba}/identitas")
        ref.set({
            "nama": data.get('nama'),
            "umur": data.get('umur'),
            "jenis_kelamin": data.get('jenis_kelamin'),
            "keturunan": data.get('keturunan')
        })

        return jsonify({"message": "✅ Identitas domba berhasil disimpan"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =========================================
# ✅ **Endpoint untuk mengambil identitas domba**
# =========================================
@app.route('/api/identity/<id_domba>', methods=['GET'])
def get_identity(id_domba):
    ref = db.reference(f"/domba/{id_domba}/identitas")
    data = ref.get()

    if data:
        return jsonify({"id_domba": id_domba, "identitas": data}), 200
    return jsonify({"error": "❌ Identitas tidak ditemukan"}), 404

# =========================================
# ✅ **Menjalankan aplikasi Flask**
# =========================================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Gunakan PORT dari environment Railway
    app.run(host='0.0.0.0', port=port, debug=True)
