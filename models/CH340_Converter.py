import serial
import serial.tools.list_ports
import time


class CH340Converter:
    # CH340 Converter röle komutları
    CH340_RELAY = {
        1: {"on": b'\xA0\x01\x01\xA2', "off": b'\xA0\x01\x00\xA1'}
    }

    def __init__(self):
        self.port = None
        self.find_device()

    def find_device(self):
        """CH340 seri portunu bulur"""
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if port.vid == 0x1a86 and port.pid == 0x7523:
                self.port = port.device
                return
        raise Exception("CH340 Converter seri portu bulunamadı")

    def control_relay_serial(self, relay_commands, relay_delay=3):
        """Seri port ile röle kontrolü"""
        try:
            with serial.Serial(self.port, baudrate=9600, timeout=1) as ser:
                # Röle aç
                ser.write(relay_commands[1]["on"])
                print(f"CH340 Converter röle açıldı: {relay_commands[1]['on'].hex()}")
                
                time.sleep(relay_delay)
                
                # Röle kapat
                ser.write(relay_commands[1]["off"])
                print(f"CH340 Converter röle kapatıldı: {relay_commands[1]['off'].hex()}")
                return True
                
        except Exception as e:
            print(f"CH340 seri port kontrolünde hata: {e}")
            return False

    def trigger_relays(self, ip=None, port=None, relay_number=None, duration=3):
        """Ana tetik fonksiyonu - RelayControl interface'i ile uyumlu"""
        print("CH340 Converter röle tetikleniyor...")
        return self.control_relay_serial(self.CH340_RELAY, relay_delay=duration)