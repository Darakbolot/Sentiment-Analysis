from flask import Flask, jsonify
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "processed"

app = Flask(__name__)

def load_json_data(filename):
    """
    Fungsi pembantu untuk memuat dan mem-parsing data dari file JSON.
    Mengembalikan data yang berhasil dimuat atau dictionary error.
    """
    try:
        # Menambahkan encoding='utf-8' untuk membaca file dengan benar
        with open(DATA_DIR / filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"error": f"File '{filename}' tidak ditemukan."}
    except json.JSONDecodeError:
        return {"error": f"Gagal mem-parsing file '{filename}'. Pastikan format JSON valid."}

@app.route('/api/berita', methods=['GET'])
def get_berita():
    """Endpoint untuk menyajikan data dari berita_analysis_result.json."""
    # Membaca file setiap kali ada request untuk memastikan data selalu fresh
    berita_data = load_json_data('berita_analysis_result.json')

    if "error" in berita_data:
        # Mengembalikan error dengan status 500 (Internal Server Error) lebih sesuai
        return jsonify(berita_data), 500

    response = {
        "status": "berhasil",
        "data": berita_data
    }
    return jsonify(response), 200

@app.route('/api/sentiment', methods=['GET'])
def get_sentiment():
    """Endpoint untuk menyajikan data dari sentiment_analysis_result.json."""
    # Membaca file setiap kali ada request untuk memastikan data selalu fresh
    sentiment_data = load_json_data('sentiment_analysis_result.json')

    if "error" in sentiment_data:
        # Mengembalikan error dengan status 500
        return jsonify(sentiment_data), 500

    response = {
        "status": "berhasil",
        "data": sentiment_data
    }
    return jsonify(response), 200

if __name__ == '__main__':
    # Menjalankan aplikasi pada port 5000 dalam mode debug
    app.run(debug=True, port=5000)
