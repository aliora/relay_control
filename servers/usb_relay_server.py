import socket
import subprocess
import sys
import os
from flask import Flask, jsonify, request

# Ana proje dizinini Python path'e ekle
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from models.USB_Relay_IO import USBRelayIO

app = Flask(__name__)

# USB Relay kontrolcü instance'ı
usb_relay = USBRelayIO()

class USBRelayServer:
    def __init__(self, host='0.0.0.0', port=9747):
        self.host = host
        self.port = port

    def start_socket_server(self):
        """Socket sunucusu başlatır - diğer embedded sunucularla uyumlu"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((self.host, self.port))
                s.listen()
                
                print(f"USB Relay Socket sunucusu başlatıldı. Dinleniyor: {self.host}:{self.port}...")
                
                while True:
                    conn, addr = s.accept()
                    with conn:
                        print(f"Bağlantı kuruldu: {addr}")
                        data = conn.recv(1024)
                        if data:
                            try:
                                relay_number = int(data.decode())
                                print(f"Alınan röle numarası: {relay_number}")
                                
                                # USB Relay tetikle
                                success = usb_relay.trigger_relays('', 0, relay_number=relay_number)
                                
                                if success:
                                    conn.sendall(b"USB Relay tetiklendi.")
                                else:
                                    conn.sendall(b"USB Relay tetikleme hatasi.")
                                    
                            except ValueError:
                                conn.sendall(b"Gecersiz relay numarasi.")
                        else:
                            print("Veri alınamadı.")
                            
        except KeyboardInterrupt:
            print("Sunucu kapatılıyor...")
        except Exception as e:
            print(f"Socket sunucu hatası: {e}")
        finally:
            print("Socket sunucu temizlendi.")

# Flask HTTP API Endpoints
@app.route('/trigger', methods=['POST'])
def trigger_relay_http():
    """
    HTTP POST isteği geldiğinde USB röle tetiklenir.
    JSON formatında relay_number ve duration parametreleri alabilir.
    
    Örnek kullanım:
    curl -X POST http://localhost:9747/trigger
    curl -X POST http://localhost:9747/trigger -H "Content-Type: application/json" -d '{"relay_number": 1, "duration": 500}'
    """
    try:
        # JSON verisini al
        json_data = request.get_json()
        
        if json_data:
            relay_number = json_data.get('relay_number', 1)
            duration = json_data.get('duration', 1000)  # millisaniye
        else:
            relay_number = 1
            duration = 1000
        
        print(f"HTTP isteği alındı - Röle: {relay_number}, Süre: {duration}ms")
        
        # USB Relay tetikle
        success = usb_relay.trigger_relays('', 0, relay_number=relay_number, duration=duration)
        
        if success:
            response = {
                "status": "success",
                "message": f"USB röle {relay_number} başarıyla tetiklendi.",
                "relay_number": relay_number,
                "duration": duration
            }
            return jsonify(response), 200
        else:
            response = {
                "status": "error",
                "message": "USB röle tetikleme başarısız.",
                "relay_number": relay_number
            }
            return jsonify(response), 500

    except Exception as e:
        response = {
            "status": "error",
            "message": f"Sunucu hatası: {e}"
        }
        return jsonify(response), 500

@app.route('/status', methods=['GET'])
def get_status():
    """
    Sunucu durumu ve kullanılabilir cihazları döner
    """
    try:
        # USB cihazlarını tara
        found_devices = usb_relay._find_usb_devices()
        
        response = {
            "status": "online",
            "message": "USB Relay sunucusu çalışıyor",
            "available_devices": list(found_devices.keys()),
            "supported_devices": list(usb_relay.TARGET_DEVICES.keys())
        }
        return jsonify(response), 200
        
    except Exception as e:
        response = {
            "status": "error",
            "message": f"Durum kontrolü hatası: {e}"
        }
        return jsonify(response), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Basit health check endpoint'i
    """
    return jsonify({"status": "healthy", "service": "usb_relay_server"}), 200

def main():
    """Ana fonksiyon - sunucu tipini seç"""
    import argparse
    
    parser = argparse.ArgumentParser(description='USB Relay Server')
    parser.add_argument('--mode', choices=['http', 'socket'], default='http',
                      help='Sunucu modu: http (Flask) veya socket')
    parser.add_argument('--host', default='0.0.0.0', help='Sunucu host adresi')
    parser.add_argument('--port', type=int, default=9747, help='Sunucu portu')
    
    args = parser.parse_args()
    
    if args.mode == 'socket':
        # Socket sunucusu çalıştır
        server = USBRelayServer(args.host, args.port)
        server.start_socket_server()
    else:
        # HTTP sunucusu çalıştır (Flask)
        print(f"USB Relay HTTP sunucusu başlatılıyor: {args.host}:{args.port}")
        app.run(host=args.host, port=args.port, debug=False)

if __name__ == '__main__':
    main()