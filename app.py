import subprocess
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/trigger', methods=['POST'])
def trigger_relay():
    """
    HTTP POST isteği geldiğinde Main_relay.py betiğini çalıştırır.
    """
    try:
        # Alt süreci (sub-process) başlat
        # Betiği argüman göndermeden çalıştır.
        result = subprocess.run(
            ['python3', 'relay_control.py'],
            capture_output=True,
            text=True,
            check=True,
            # Çalışma dizinini, betiğinizin bulunduğu dizine ayarlayın
            cwd='/home/visioai/Projects/alpr-client/relay_control'
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
    # Uygulamayı 0.0.0.0 IP'sinde ve 9747 portunda çalıştır
    app.run(host='0.0.0.0', port=9747)