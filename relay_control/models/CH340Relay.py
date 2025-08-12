import serial
import serial.tools.list_ports
import time

# CH340 röle kontrol modeli

class CH340Relay:
    RELAY_COMMANDS = {
        1: {"on": b'\xA0\x01\x01\xA2', "off": b'\xA0\x01\x00\xA1'}
    }
    RELAY_DELAY = 1

    @staticmethod
    def find_ports():
        ports = serial.tools.list_ports.comports()
        ch340_ports = [port for port in ports if port.vid == 0x1a86 and port.pid == 0x7523]
        ch340_ports.sort(key=lambda p: p.device)
        return ch340_ports

    @classmethod
    def trigger(cls, relay_number=1, device_index=0):
        ports = cls.find_ports()
        if device_index >= len(ports):
            print(f"CH340 cihaz index {device_index} bulunamadı.")
            return False
        target_port = ports[device_index].device
        print(f"CH340 Converter seçildi: {target_port}")
        try:
            with serial.Serial(target_port, baudrate=9600, timeout=1) as ser:
                ser.write(cls.RELAY_COMMANDS[relay_number]["on"])
                print(f"CH340 röle açıldı: {cls.RELAY_COMMANDS[relay_number]['on'].hex()}")
                time.sleep(cls.RELAY_DELAY)
                ser.write(cls.RELAY_COMMANDS[relay_number]["off"])
                print(f"CH340 röle kapatıldı: {cls.RELAY_COMMANDS[relay_number]['off'].hex()}")
            return True
        except Exception as e:
            print(f"CH340 röle kontrolünde hata: {e}")
            return False
