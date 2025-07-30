import usb.core
import usb.util

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

    # Hiçbir cihaz bulunamazsa uyarı
    if not found_usb_devices:
        print("Hiçbir cihaz bulunamadı")