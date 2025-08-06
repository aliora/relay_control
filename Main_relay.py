import usb.core
import usb.util
import serial
import serial.tools.list_ports
import time

# GLOBAL: Sabit değerler
RELAY_DELAY = 1  # seconds

# CLASS: Röle komut yapısı
class RelayCommands:
    RELAY_COMMANDS = {
        1: {"on": b'\xA0\x01\x01\xA2', "off": b'\xA0\x01\x00\xA1'}
    }

def control_relay_device(device, relay_commands, device_type="CH340"):
    try:
        if device_type == "CH340":
            # INIT: Port arama
            ports = serial.tools.list_ports.comports()
            target_port = None
            
            # SEARCH: VID/PID kontrol
            for port in ports:
                if port.vid == 0x1a86 and port.pid == 0x7523:
                    target_port = port.device
                    break
            
            # ERROR: Port bulunamadı
            if target_port is None:
                print("CH340 seri portu bulunamadı")
                return False
                
            # CONNECT: Seri port
            with serial.Serial(target_port, baudrate=9600, timeout=1) as ser:
                # CMD: Röle aç
                ser.write(relay_commands[1]["on"])
                print(f"CH340 Converter röle açıldı: {relay_commands[1]['on'].hex()}")
                
                # Belirlenen süre kadar bekle
                print(f"Röle {RELAY_DELAY} saniye açık kalacak...")
                time.sleep(RELAY_DELAY)
                
                # CMD: Röle kapat
                ser.write(relay_commands[1]["off"])
                print(f"CH340 Converter röle kapatıldı: {relay_commands[1]['off'].hex()}")
                return True
                
        elif device_type == "MSR":
            try:
                # INIT: USB reset
                device.reset()
                
                # CONFIG: Driver ayarları
                for interface in [0, 1]:
                    if device.is_kernel_driver_active(interface):
                        device.detach_kernel_driver(interface)
                
                # CONFIG: USB ayarları
                device.set_configuration()
                usb.util.claim_interface(device, 0)
                
                # INIT: Endpoint bulma
                cfg = device.get_active_configuration()
                intf = cfg[(0,0)]
                ep = usb.util.find_descriptor(
                    intf,
                    custom_match = \
                    lambda e: \
                        usb.util.endpoint_direction(e.bEndpointAddress) == \
                        usb.util.ENDPOINT_OUT
                )
                
                if ep is None:
                    raise RuntimeError('MSR Endpoint bulunamadı')
                
                # CMD: Röle aç
                ep.write(relay_commands[1]["on"])
                print(f"MSR Reader röle açıldı: {relay_commands[1]['on'].hex()}")
                
                # Belirlenen süre kadar bekle
                print(f"Röle {RELAY_DELAY} saniye açık kalacak...")
                time.sleep(RELAY_DELAY)
                
                # CMD: Röle kapat
                ep.write(relay_commands[1]["off"])
                print(f"MSR Reader röle kapatıldı: {relay_commands[1]['off'].hex()}")
                return True
                
            except usb.core.USBError as e:
                if e.errno == 16:
                    print("Cihaz meşgul. Yeniden bağlamayı deneyin veya:")
                    print("1. lsusb ile cihazı kontrol edin")
                    print("2. sudo rmmod usbserial")
                    print("3. Cihazı çıkarıp tekrar takın")
                elif e.errno == 13:
                    print("Yetki hatası: USB cihazına erişim için root yetkisi gerekiyor")
                    print("udev kurallarını eklediğinizden emin olun")
                else:
                    print(f"MSR USB hatası: {e}")
                return False
            
    except Exception as e:
        print(f"{device_type} röle kontrolünde hata: {e}")
        return False

def find_usb_devices(device_list):

    found_devices = {}
    
    for device_name, (vendor_id, product_id) in device_list.items():
        # Tüm eşleşen cihazları bul
        devices = list(usb.core.find(find_all=True, idVendor=vendor_id, idProduct=product_id))
        
        if devices:
            if len(devices) == 1:
                found_devices[device_name] = devices[0]
            else:
                # Birden fazla aynı cihaz varsa, hepsini listele
                found_devices[device_name] = devices
                print(f"Bulundu {len(devices)} adet {device_name}:")
                for i, dev in enumerate(devices, 1):
                    print(f"  {device_name}_{i}: {dev}")
        else:
            print(f"Bulundu {len(devices) + 1} adet bulunu")
    return found_devices

class RelayControl:
    def __init__(self):
        self.target_devices = {
            "MSR_Reader": (0x5131, 0x2007),
            "CH340_Converter": (0x1a86, 0x7523),
        }

    def trigger_relay(self, ip, port, relay_number=None, duration=100):
        print("Röle kontrolü tetiklendi.")
        found_devices = find_usb_devices(self.target_devices)
        
        if not found_devices:
            print("Hiçbir cihaz bulunamadı")
            return
            
        for device_name, device in found_devices.items():
            if device_name == "MSR_Reader":
                print("MSR Reader bulundu. Kontrol ediliyor.")
                control_relay_device(device, RelayCommands.RELAY_COMMANDS, device_type="MSR")
            elif device_name == "CH340_Converter":
                print("CH340 Converter bulundu. Kontrol ediliyor.")
                control_relay_device(device, RelayCommands.RELAY_COMMANDS, device_type="CH340")