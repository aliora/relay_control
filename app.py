from flask import Flask, jsonify, request  # request'i ekledik
import subprocess
from flask_cors import CORS
import logging  # Logging ekledik

app = Flask(__name__)
CORS(app)

# Logging ayarları ekledik
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/trigger', methods=['POST'])
def trigger_relay():
    """
    HTTP POST isteği geldiğinde relay_control.py betiğini çalıştırır.
    İsteğe bağlı olarak relay numarası parametresi alabilir.
    """
    try:
        # POST verilerini al (YENİ)
        try:
            data = request.get_json() or {}
            relay_number = data.get('relayNumber', None)
            logger.info(f"Received request with relay number: {relay_number}")
        except Exception as e:
            logger.warning(f"JSON parse error (using default): {e}")
            relay_number = None

        # Komutu hazırla
        cmd = ['python3', 'relay_control.py']
        
        # Eğer relay numarası varsa, argüman olarak ekle (YENİ)
        if relay_number:
            cmd.append(str(relay_number))

        logger.info(f"Executing command: {' '.join(cmd)}")

        # Alt süreci başlat - timeout ekledik
        result = subprocess.run(
            cmd,  # Değişken komut kullanıyoruz
            capture_output=True,
            text=True,
            check=True,
            timeout=30,  # 30 saniye timeout ekledik
            cwd='/home/visioai/Projects/alpr-client/relay_control'
        )

        logger.info(f"Script executed successfully. Output: {result.stdout}")

        # Betiğin başarılı bir şekilde çalıştığını belirten yanıt - geliştirildi
        response = {
            "status": "success",
            "message": "relay_control.py betiği başarıyla çalıştırıldı.",
            "relayNumber": relay_number,  # YENİ
            "stdout": result.stdout.strip(),  # strip() ekledik
            "stderr": result.stderr.strip() if result.stderr else None  # YENİ
        }
        return jsonify(response), 200

    except subprocess.TimeoutExpired:  # YENİ hata türü
        logger.error("Script execution timeout")
        response = {
            "status": "error",
            "message": "Betik çalıştırılırken zaman aşımı oluştu."
        }
        return jsonify(response), 408

    except subprocess.CalledProcessError as e:
        # Hata mesajları geliştirildi
        logger.error(f"Script execution error: {e}")
        response = {
            "status": "error",
            "message": f"Betik çalıştırılırken hata oluştu: {e}",
            "stderr": e.stderr,
            "returncode": e.returncode  # YENİ
        }
        return jsonify(response), 500

    except Exception as e:
        # Hata mesajı geliştirildi
        logger.error(f"Server error: {e}")
        response = {
            "status": "error",
            "message": f"Sunucu hatası: {str(e)}"
        }
        return jsonify(response), 500

# YENİ endpoint - sağlık kontrolü için
@app.route('/health', methods=['GET'])
def health_check():
    """Sunucu durumunu kontrol etmek için basit bir endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Flask relay server is running"
    }), 200

if __name__ == '__main__':
    logger.info("Starting Flask relay server on 0.0.0.0:9747")  # Başlangıç mesajı
    # debug=True ekledik (geliştirme için)
    app.run(host='0.0.0.0', port=9747, debug=True)