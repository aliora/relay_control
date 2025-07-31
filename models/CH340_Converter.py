import usb.core
import usb.util
import serial
import serial.tools.list_ports
import time


class CH340Converter:
    def __init__(self):
        # CH340 Converter röle komutları - Main_relay.py'den alınmış
        self.CH340_RELAY = {
            1: {"on": b'\xA0\x01\x01\xA2', "off": b'\xA0\x01\x00\xA1'}
        }

    def find_usb_devices(self):
        """USB üzerinden CH340 cihazını bulur - Main_relay.py'den alınmış"""
        target_devices = {
            "CH340_Converter": (0x1a86, 0x7523)
        }
        
        found_devices = {}
        
        for device_name, (vendor_id, product_id) in target_devices.items():
            devices = list(usb.core.find(find_all=True, idVendor=vendor_id, idProduct=product_id))
            
            if devices:
                if len(devices) == 1:
                    found_devices[device_name] = devices[0]
                    print(f"1 adet {device_name} bulundu")
                else:
                    found_devices[device_name] = devices
                    print(f"Bulundu {len(devices)} adet {device_name}")
            else:
                print(f"{device_name} bulunamadı")
                
        return found_devices

    def control_relay_device(self, device, relay_commands, relay_delay=3):
        """
        Main_relay.py'den alınmış CH340 kontrol fonksiyonu
        """
        try:
            # CH340 için seri port bağlantısı bul
            ports = serial.tools.list_ports.comports()
            target_port = None
            
            for port in ports:
                # CH340 cihazını VID:PID ile tanımla
                if port.vid == 0x1a86 and port.pid == 0x7523:
                    target_port = port.device
                    break
            
            if target_port is None:
                print("CH340 seri portu bulunamadı")
                return False
                
            # Seri port bağlantısı aç ve komutları gönder
            with serial.Serial(target_port, baudrate=9600, timeout=1) as ser:
                # Röle aç
                ser.write(relay_commands[1]["on"])
                print(f"CH340 Converter röle açıldı: {relay_commands[1]['on'].hex()}")
                
                # Belirlenen süre kadar bekle
                print(f"Röle {relay_delay} saniye açık kalacak...")
                time.sleep(relay_delay)
                
                # Röle kapat
                ser.write(relay_commands[1]["off"])
                print(f"CH340 Converter röle kapatıldı: {relay_commands[1]['off'].hex()}")
                return True
                
        except Exception as e:
            print(f"CH340 röle kontrolünde hata: {e}")
            return False

    def trigger_relays(self, ip=None, port=None, relay_number=None, duration=3):
        """
        Ana tetik fonksiyonu - RelayControl interface'i ile uyumlu
        Main_relay.py'deki kodun adaptasyonu
        """
        print("CH340 Converter cihazı aranıyor...")
        
        # USB cihazını bul
        found_devices = self.find_usb_devices()
        
        if "CH340_Converter" in found_devices:
            print("CH340 Converter bulundu, röle tetikleniyor...")
            device = found_devices["CH340_Converter"]
            
            # Röle kontrolünü çalıştır
            return self.control_relay_device(device, self.CH340_RELAY, relay_delay=duration)
        else:
            print("CH340 Converter cihazı bulunamadı")
            return False