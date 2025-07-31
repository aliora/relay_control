import usb.core
import usb.util
import serial
import serial.tools.list_ports
import time


class CH340Converter:
    def __init__(self):
        # CH340 Converter röle komutları
        self.CH340_RELAY = {
            1: {"on": b'\xA0\x01\x01\xA2', "off": b'\xA0\x01\x00\xA1'}
        }
        self.device = None
        self.port = None

    def find_usb_device(self):
        """USB üzerinden CH340 cihazını bulur"""
        try:
            device = usb.core.find(idVendor=0x1a86, idProduct=0x7523)
            if device is not None:
                self.device = device
                print("CH340 USB cihazı bulundu")
                return True
            else:
                print("CH340 USB cihazı bulunamadı")
                return False
        except Exception as e:
            print(f"USB cihaz arama hatası: {e}")
            return False

    def find_serial_port(self):
        """CH340 seri portunu bulur"""
        try:
            ports = serial.tools.list_ports.comports()
            for port in ports:
                if port.vid == 0x1a86 and port.pid == 0x7523:
                    self.port = port.device
                    print(f"CH340 seri portu bulundu: {self.port}")
                    return True
            print("CH340 seri portu bulunamadı")
            return False
        except Exception as e:
            print(f"Seri port arama hatası: {e}")
            return False

    def connect(self):
        """CH340 bağlantısını kur"""
        if not self.find_usb_device():
            return False
        if not self.find_serial_port():
            return False
        return True

    def send_command(self, command):
        """Seri port üzerinden komut gönder"""
        try:
            with serial.Serial(self.port, baudrate=9600, timeout=1) as ser:
                ser.write(command)
                print(f"Komut gönderildi: {command.hex()}")
                return True
        except Exception as e:
            print(f"Komut gönderme hatası: {e}")
            return False

    def trigger_relays(self, ip=None, port=None, relay_number=1, duration=3):
        """
        Ana tetik fonksiyonu - RL-02 benzeri yapı
        """
        print("CH340 Converter röle tetikleniyor...")
        
        # Bağlantıyı kur
        if not self.connect():
            print("CH340 bağlantısı kurulamadı")
            return False

        try:
            # Röle açma komutu
            if not self.send_command(self.CH340_RELAY[relay_number]["on"]):
                return False
            print(f"CH340 röle {relay_number} açıldı")
            
            # Belirlenen süre kadar bekle
            print(f"Röle {duration} saniye açık kalacak...")
            time.sleep(duration)
            
            # Röle kapatma komutu
            if not self.send_command(self.CH340_RELAY[relay_number]["off"]):
                return False
            print(f"CH340 röle {relay_number} kapatıldı")
            
            return True
            
        except Exception as e:
            print(f"CH340 röle kontrolünde hata: {e}")
            return False