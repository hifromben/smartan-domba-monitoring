from flask import Flask, request, jsonify, send_from_directory, abort
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db
import os

# Inisialisasi Flask
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Inisialisasi Firebase
cred = credentials.Certificate("firebase_credentials.json")  # Pastikan file ini ada
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://smartan-domba-garut-default-rtdb.asia-southeast1.firebasedatabase.app'
})

# ==============================================
# ✅ **Endpoint untuk menyimpan data sensor ke Firebase**
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

        # Simpan data ke Firebase
        ref = db.reference(f'/sensor/{id_domba}')
        ref.push({
            "berat": berat,
            "suhu": suhu,
            "tinggi": tinggi
        })

        # Emit data terbaru ke client melalui Socket.IO (Real-time update)
        socketio.emit('sensor_update', {"berat": berat, "suhu": suhu, "tinggi": tinggi})

        return jsonify({"message": "✅ Data berhasil disimpan"}), 201
    except Exception as e:
        print("❌ Error saat menyimpan data sensor:", str(e))
        return jsonify({"error": str(e)}), 500

# =================================================
# ✅ **Endpoint untuk mengambil data sensor dari Firebase**
# =================================================
@app.route('/api/sensor/<id_domba>', methods=['GET'])
def get_sensor_data(id_domba):
    try:
        ref = db.reference(f'/sensor/{id_domba}')
        data = ref.get()

        if not data:
            return jsonify({"error": "❌ Data tidak ditemukan untuk ID domba ini"}), 404

        return jsonify({
            "id_domba": id_domba,
            "data": list(data.values())  # Ubah dictionary ke list
        }), 200
    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"error": str(e)}), 500

# =================================================
# ✅ **Endpoint untuk menyimpan data vaksin ke Firebase**
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

        # Simpan ke Firebase
        ref = db.reference(f'/vaccine/{id_domba}')
        ref.push({
            "jenis_vaksin": jenis_vaksin,
            "tanggal": tanggal
        })

        return jsonify({
            "message": "✅ Data vaksin berhasil disimpan"
        }), 201
    except Exception as e:
        print("❌ Error saat menyimpan data vaksin:", str(e))
        return jsonify({"error": str(e)}), 500

# =================================================
# ✅ **Endpoint untuk mengambil riwayat vaksin dari Firebase**
# =================================================
@app.route('/api/vaccine/<id_domba>', methods=['GET'])
def get_vaccine_data(id_domba):
    try:
        ref = db.reference(f'/vaccine/{id_domba}')
        data = ref.get()

        if not data:
            return jsonify({"error": "❌ Data vaksin tidak ditemukan"}), 404

        return jsonify({
            "id_domba": id_domba,
            "riwayat_vaksin": list(data.values())  # Ubah dictionary ke list
        }), 200
    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"error": str(e)}), 500

# ==========================================================
# ✅ **Endpoint untuk menghapus data vaksin berdasarkan index**
# ==========================================================
@app.route('/api/vaccine/<id_domba>/<vaccine_id>', methods=['DELETE'])
def delete_vaccine_data(id_domba, vaccine_id):
    try:
        ref = db.reference(f'/vaccine/{id_domba}/{vaccine_id}')
        if ref.get():
            ref.delete()
            return jsonify({"message": "✅ Data vaksin berhasil dihapus"}), 200
        return jsonify({"error": "❌ Data tidak ditemukan"}), 404
    except Exception as e:
        print("❌ Error saat menghapus data vaksin:", str(e))
        return jsonify({"error": str(e)}), 500

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
    port = int(os.environ.get("PORT", 5000))  # Gunakan PORT dari environment Railway
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
