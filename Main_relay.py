import usb.core
import usb.util
import serial
import serial.tools.list_ports
import time

# Global röle komutları sınıfı
class RelayCommands:
    # CH340 Converter röle komutları
    CH340_RELAY = {
        1: {"on": b'\xA0\x01\x01\xA2', "off": b'\xA0\x01\x00\xA1'}
    }
    
    # MSR Reader röle komutları (şimdilik aynı - MSR için farklı komutlar gelecek)
    MSR_RELAY = {
        1: {"on": b'\xA0\x01\x01\xA2', "off": b'\xA0\x01\x00\xA1'}  # MSR için özel binary komutlar buraya gelecek
    }

def control_relay_device(device, relay_commands, device_type="CH340", relay_delay=3):
    """
    Global röle kontrol fonksiyonu - farklı cihaz tipleri için kullanılabilir
    
    Args:
        device: USB cihaz objesi
        relay_commands: Röle komutları sözlüğü
        device_type: Cihaz tipi ("CH340" veya "MSR")
        relay_delay: Röle açık kalma süresi (saniye)
    """
    try:
        if device_type == "CH340":
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
                
        elif device_type == "MSR":
            # MSR Reader için kontrol kodu buraya gelecek
            print(f"MSR Reader röle kontrol başlatılıyor...")
            print(f"MSR ON komutu: {relay_commands[1]['on'].hex()}")  # MSR için binary komut
            print(f"MSR OFF komutu: {relay_commands[1]['off'].hex()}")  # MSR için binary komut
            
            # MSR için özel implementasyon gerekecek (USB HID veya başka protokol)
            # Şimdilik sadece bilgi yazdırıyor
            print(f"MSR röle {relay_delay} saniye açık kalacak...")
            time.sleep(relay_delay)
            print("MSR röle kapatıldı")
            return True
            
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
            print("1 adet relay bulundu")
    return found_devices

if __name__ == "__main__":
    # Hedef cihazlar - her benzersiz VID/PID çifti için tek giriş
    target_devices = {
        "MSR_Reader": (0x5131, 0x2007),
        "CH340_Converter": (0x1a86, 0x7523),  # Tek giriş
    }
    
    print("USB cihazları taranıyor...")
    found_usb_devices = find_usb_devices(target_devices)
    print("Tarama tamamlandı.")
    
    # Bulunan cihazları kontrol et ve ilgili tetik kodlarını çalıştır
    for device_name, device in found_usb_devices.items():
        if device_name == "MSR_Reader":
            print("MSR Reader")
            
            # MSR Reader için tetik kodu
            control_relay_device(device, RelayCommands.MSR_RELAY, device_type="MSR", relay_delay=3)
            
        elif device_name == "CH340_Converter":
            print("CH340 Converter")

            # CH340 Converter için tetik kodu
            control_relay_device(device, RelayCommands.CH340_RELAY, device_type="CH340", relay_delay=3)

    # Hiçbir cihaz bulunamazsa uyarı
    if not found_usb_devices:
        print("Hiçbir cihaz bulunamadı")