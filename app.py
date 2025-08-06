import subprocess
from flask import Flask, jsonify
from relay_control import RelayControl

app = Flask(__name__)

@app.route('/trigger', methods=['POST'])
def trigger_relay():
    try:
        # main-relay sınıfını çağır
        relay_controller = RelayControl('main-relay')
        relay_controller.trigger_relay('0.0.0.0', 9747) # IP ve port değerlerini buraya ekleyebilirsiniz
        
        response = {
            "status": "success",
            "message": "Röle kontrolü başarıyla tamamlandı.",
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