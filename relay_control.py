import usb.core
import usb.util
import serial
import serial.tools.list_ports
import time
import sys

# GLOBAL: Sabit değerler
RELAY_DELAY = 1  # seconds

# CLASS: Röle komut yapısı
class RelayCommands:
    RELAY_COMMANDS = {
        1: {"on": b'\xA0\x01\x01\xA2', "off": b'\xA0\x01\x00\xA1'}
    }

def control_relay_device(device, relay_commands, device_type="CH340", device_index=0):
    try:
        if device_type == "CH340":
            # INIT: Port arama
            ports = serial.tools.list_ports.comports()
            ch340_ports = []
            
            # SEARCH: VID/PID kontrol - tüm CH340 portlarını bul
            for port in ports:
                if port.vid == 0x1a86 and port.pid == 0x7523:
                    ch340_ports.append(port.device)
            
            # ERROR: Port bulunamadı
            if not ch340_ports:
                print("CH340 seri portu bulunamadı")
                return False
            
            # Belirtilen index'teki portu seç
            if device_index >= len(ch340_ports):
                print(f"CH340 cihaz index {device_index} bulunamadı. Mevcut cihaz sayısı: {len(ch340_ports)}")
                return False
                
            target_port = ch340_ports[device_index]
            print(f"CH340 Converter #{device_index + 1} seçildi: {target_port}")
                
            # CONNECT: Seri port
            with serial.Serial(target_port, baudrate=9600, timeout=1) as ser:
                # CMD: Röle aç
                ser.write(relay_commands[1]["on"])
                print(f"CH340 Converter #{device_index + 1} röle açıldı: {relay_commands[1]['on'].hex()}")
                
                # Belirlenen süre kadar bekle
                print(f"Röle {RELAY_DELAY} saniye açık kalacak...")
                time.sleep(RELAY_DELAY)
                
                # CMD: Röle kapat
                ser.write(relay_commands[1]["off"])
                print(f"CH340 Converter #{device_index + 1} röle kapatıldı: {relay_commands[1]['off'].hex()}")
                return True
                
        elif device_type == "MSR":
            try:
                # Eğer birden fazla MSR cihazı varsa, belirtilen index'i seç
                if isinstance(device, list):
                    if device_index >= len(device):
                        print(f"MSR cihaz index {device_index} bulunamadı. Mevcut cihaz sayısı: {len(device)}")
                        return False
                    selected_device = device[device_index]
                    print(f"MSR Reader #{device_index + 1} seçildi")
                else:
                    selected_device = device
                    print("MSR Reader seçildi")
                
                # INIT: USB reset
                selected_device.reset()
                
                # CONFIG: Driver ayarları
                for interface in [0, 1]:
                    if selected_device.is_kernel_driver_active(interface):
                        selected_device.detach_kernel_driver(interface)
                
                # CONFIG: USB ayarları
                selected_device.set_configuration()
                usb.util.claim_interface(selected_device, 0)
                
                # INIT: Endpoint bulma
                cfg = selected_device.get_active_configuration()
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
                print(f"MSR Reader #{device_index + 1} röle açıldı: {relay_commands[1]['on'].hex()}")
                
                # Belirlenen süre kadar bekle
                print(f"Röle {RELAY_DELAY} saniye açık kalacak...")
                time.sleep(RELAY_DELAY)
                
                # CMD: Röle kapat
                ep.write(relay_commands[1]["off"])
                print(f"MSR Reader #{device_index + 1} röle kapatıldı: {relay_commands[1]['off'].hex()}")
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
            found_devices[device_name] = devices
            print(f"Bulundu {len(devices)} adet {device_name}")
            for i, dev in enumerate(devices, 1):
                print(f"  {device_name}_{i}: {dev}")
        else:
            print(f"{device_name} bulunamadı")
    return found_devices

def trigger_specific_relay(relay_number):
    """
    Belirtilen relay numarasına göre ilgili cihazı tetikler.
    relay_number: 1-4 arası değer
    """
    target_devices = {
        "MSR_Reader": (0x5131, 0x2007),
        "CH340_Converter": (0x1a86, 0x7523),
    }
    
    print(f"Relay #{relay_number} tetikleniyor...")
    print("USB cihazları taranıyor...")
    found_usb_devices = find_usb_devices(target_devices)
    print("Tarama tamamlandı.")
    
    # Tüm cihazları say
    total_devices = 0
    device_mapping = []
    
    # MSR cihazlarını ekle
    if "MSR_Reader" in found_usb_devices:
        msr_devices = found_usb_devices["MSR_Reader"]
        for i in range(len(msr_devices)):
            total_devices += 1
            device_mapping.append(("MSR", i))
            print(f"Cihaz {total_devices}: MSR Reader #{i + 1}")
    
    # CH340 cihazlarını ekle
    if "CH340_Converter" in found_usb_devices:
        ports = serial.tools.list_ports.comports()
        ch340_count = sum(1 for port in ports if port.vid == 0x1a86 and port.pid == 0x7523)
        for i in range(ch340_count):
            total_devices += 1
            device_mapping.append(("CH340", i))
            print(f"Cihaz {total_devices}: CH340 Converter #{i + 1}")
    
    if total_devices == 0:
        print("Hiçbir relay cihazı bulunamadı!")
        return False
    
    print(f"Toplam {total_devices} relay cihazı bulundu.")
    
    # Relay numarasını kontrol et
    if relay_number < 1 or relay_number > total_devices:
        print(f"Geçersiz relay numarası: {relay_number}. Mevcut aralık: 1-{total_devices}")
        return False
    
    # Belirtilen relay'i tetikle
    device_type, device_index = device_mapping[relay_number - 1]
    
    if device_type == "MSR":
        return control_relay_device(found_usb_devices["MSR_Reader"], RelayCommands.RELAY_COMMANDS, device_type="MSR", device_index=device_index)
    elif device_type == "CH340":
        return control_relay_device(found_usb_devices["CH340_Converter"], RelayCommands.RELAY_COMMANDS, device_type="CH340", device_index=device_index)
    
    return False

# ==============================
# RelayControl Wrapper Class - DÜZELTİLDİ
# ==============================
class RelayControl:
    def __init__(self, brand=None):  # brand parametresi eklendi
        self.brand = brand or "CH340"  # Default olarak CH340
        self.commands = RelayCommands.RELAY_COMMANDS

    def triggerRelays(self, ip=None, port=None, relayNumber=None, duration=None):
        """JavaScript API'si ile uyumlu method"""
        if relayNumber:
            return trigger_specific_relay(relayNumber)
        else:
            # Eski davranış - brand'e göre tetikle
            return self.trigger()

    def trigger(self, device_type=None):
        """Eski API ile uyumluluk için"""
        device_type = device_type or self.brand
        target_devices = {
            "MSR_Reader": (0x5131, 0x2007),
            "CH340_Converter": (0x1a86, 0x7523),
        }
        found_devices = find_usb_devices(target_devices)
        if device_type == "MSR" and "MSR_Reader" in found_devices:
            return control_relay_device(found_devices["MSR_Reader"], self.commands, device_type="MSR")
        elif device_type in ["CH340", "MSR-CH340"] and "CH340_Converter" in found_devices:
            return control_relay_device(found_devices["CH340_Converter"], self.commands, device_type="CH340")
        return False

if __name__ == "__main__":
    # Komut satırı argümanını kontrol et
    if len(sys.argv) > 1:
        try:
            relay_number = int(sys.argv[1])
            print(f"Komut satırından alınan relay numarası: {relay_number}")
            success = trigger_specific_relay(relay_number)
            if success:
                print(f"Relay #{relay_number} başarıyla tetiklendi!")
            else:
                print(f"Relay #{relay_number} tetiklenemedi!")
                sys.exit(1)
        except ValueError:
            print("Geçersiz relay numarası! Lütfen 1-4 arası bir sayı girin.")
            sys.exit(1)
    else:
        # Argüman yoksa tüm cihazları tetikle (eski davranış)
        target_devices = {
            "MSR_Reader": (0x5131, 0x2007),
            "CH340_Converter": (0x1a86, 0x7523),
        }
        
        print("USB cihazları taranıyor...")
        found_usb_devices = find_usb_devices(target_devices)
        print("Tarama tamamlandı.")
        
        # Bulunan cihazları kontrol et ve ilgili tetik kodlarını çalıştır
        for device_name, device in found_usb_devices.items():
            if device_name == "MSR_Reader":
                print("MSR Reader")
                control_relay_device(device, RelayCommands.RELAY_COMMANDS, device_type="MSR")
            elif device_name == "CH340_Converter":
                print("CH340 Converter")
                control_relay_device(device, RelayCommands.RELAY_COMMANDS, device_type="CH340")

        # Hiçbir cihaz bulunamazsa uyarı
        if not found_usb_devices:
            print("Hiçbir cihaz bulunamadı")