import subprocess
from flask import Flask, jsonify
from relay_control.Main_relay import RelayControl

app = Flask(__name__)

@app.route('/trigger', methods=['POST'])
def trigger_relay():
    try:
        # Main_relay.py içindeki sınıfı çağır
        relay_controller = RelayControl()
        relay_controller.trigger_relay()
        
        response = {
            "status": "success",
            "message": "Main_relay.py betiği başarıyla çalıştırıldı.",
            "stdout": "Röle kontrolü başarıyla tamamlandı."
        }
        return jsonify(response), 200

    except Exception as e:
        response = {
            "status": "error",
            "message": f"Sunucu veya röle kontrol hatası: {e}"
        }
        return jsonify(response), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9747)
    # MSR Reader cihazı için röle kontrolü