import usb.core
import usb.util
import serial
import serial.tools.list_ports
import time

def control_ch340_relay(device, relay_command):
    """
    CH340 Converter üzerinden röle kontrolü yapar
    
    Args:
        device: USB cihaz objesi
        relay_command: Röle komutu (b'\xA0\x01\x01\xA2' açmak için, b'\xA0\x01\x00\xA1' kapatmak için)
    """
    try:
        # CH340 için seri port bağlantısı bul
        ports = serial.tools.list_ports.comports()
        ch340_port = None
        
        for port in ports:
            # CH340 cihazını VID:PID ile tanımla
            if port.vid == 0x1a86 and port.pid == 0x7523:
                ch340_port = port.device
                break
        
        if ch340_port is None:
            print("CH340 seri portu bulunamadı")
            return False
            
        # Seri port bağlantısı aç
        with serial.Serial(ch340_port, baudrate=9600, timeout=1) as ser:
            # Röle komutunu gönder
            ser.write(relay_command)
            print(f"CH340 Converter'a komut gönderildi: {relay_command.hex()}")
            return True
            
    except Exception as e:
        print(f"CH340 röle kontrolünde hata: {e}")
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
            
        elif device_name == "CH340_Converter":
            print("CH340 Converter")

            # CH340 Converter için tetik kodu
            relay_commands = {
                1: {"on": b'\xA0\x01\x01\xA2', "off": b'\xA0\x01\x00\xA1'}
            }
            
            relay_delay = 3  # Röle açık kalma süresi (saniye)
            
            # Röle 1'i aç
            control_ch340_relay(device, relay_commands[1]["on"])
            
            # Belirlenen süre kadar bekle
            print(f"Röle {relay_delay} saniye açık kalacak...")
            time.sleep(relay_delay)
            
            # Röle 1'i kapat
            control_ch340_relay(device, relay_commands[1]["off"])
            print("Röle kapatıldı")

    # Hiçbir cihaz bulunamazsa uyarı
    if not found_usb_devices:
        print("Hiçbir cihaz bulunamadı")