import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/trigger', methods=['POST'])
def trigger_relay():
    """
    HTTP POST isteği ile Main_relay.py betiğini çalıştırır.
    """
    try:
        # Alt süreci (sub-process) başlat
        # Python betiğinin çıktısını yakalamak için subprocess.run kullanılır.
        # check=True, hata durumunda istisna fırlatılmasını sağlar.
        result = subprocess.run(
            ['python3', 'Main_relay.py'],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Betiğin başarılı bir şekilde çalıştığını belirten yanıt
        response = {
            "status": "success",
            "message": "Main_relay.py betiği başarıyla çalıştırıldı.",
            "stdout": result.stdout
        }
        return jsonify(response), 200

    except subprocess.CalledProcessError as e:
        # Betik hata ile sonlanırsa
        response = {
            "status": "error",
            "message": f"Betik çalıştırılırken hata oluştu: {e}",
            "stderr": e.stderr
        }
        return jsonify(response), 500

    except Exception as e:
        # Diğer hatalar
        response = {
            "status": "error",
            "message": f"Sunucu hatası: {e}"
        }
        return jsonify(response), 500

if __name__ == '__main__':
    # 0.0.0.0 tüm arayüzlerde dinlemeyi sağlar
    # 9747 portu
    app.run(host='0.0.0.0', port=9747)