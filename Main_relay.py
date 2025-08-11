import usb.core
import usb.util
import serial
import serial.tools.list_ports
import time
import os

# GLOBAL: Sabit değerler
RELAY_DELAY = 1  # seconds

# CLASS: Röle komut yapısı
class RelayCommands:
    RELAY_COMMANDS = {
        1: {"on": b'\xA0\x01\x01\xA2', "off": b'\xA0\x01\x00\xA1'}
    }

def check_udev_rules():
    """Udev kurallarının varlığını kontrol et"""
    udev_file = "/etc/udev/rules.d/99-msr-relay.rules"
    if not os.path.exists(udev_file):
        print("\n⚠️  UYARI: Udev kuralları bulunamadı!")
        print("Sudo olmadan çalıştırmak için şu adımları uygulayın:")
        print("1. Şu komutu çalıştırın:")
        print("   sudo nano /etc/udev/rules.d/99-msr-relay.rules")
        print("2. Dosyaya şu satırları ekleyin:")
        print('   SUBSYSTEM=="usb", ATTR{idVendor}=="5131", ATTR{idProduct}=="2007", MODE="0666", GROUP="plugdev"')
        print('   SUBSYSTEM=="usb", ATTR{idVendor}=="1a86", ATTR{idProduct}=="7523", MODE="0666", GROUP="plugdev"')
        print("3. Kuralları yenileyin:")
        print("   sudo udevadm control --reload-rules && sudo udevadm trigger")
        print("4. Kullanıcıyı gruba ekleyin:")
        print("   sudo usermod -a -G plugdev $USER")
        print("5. Sistemi yeniden başlatın\n")
        return False
    return True

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
                print("❌ CH340 seri portu bulunamadı")
                return False
                
            # CONNECT: Seri port
            try:
                with serial.Serial(target_port, baudrate=9600, timeout=1) as ser:
                    # CMD: Röle aç
                    ser.write(relay_commands[1]["on"])
                    print(f"✅ CH340 Converter röle açıldı: {relay_commands[1]['on'].hex()}")
                    
                    # Belirlenen süre kadar bekle
                    print(f"⏳ Röle {RELAY_DELAY} saniye açık kalacak...")
                    time.sleep(RELAY_DELAY)
                    
                    # CMD: Röle kapat
                    ser.write(relay_commands[1]["off"])
                    print(f"✅ CH340 Converter röle kapatıldı: {relay_commands[1]['off'].hex()}")
                    return True
            except serial.SerialException as e:
                print(f"❌ CH340 seri port hatası: {e}")
                if "Permission denied" in str(e):
                    print("💡 İpucu: Kullanıcıyı 'dialout' grubuna ekleyin: sudo usermod -a -G dialout $USER")
                return False
                
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
                print(f"✅ MSR Reader röle açıldı: {relay_commands[1]['on'].hex()}")
                
                # Belirlenen süre kadar bekle
                print(f"⏳ Röle {RELAY_DELAY} saniye açık kalacak...")
                time.sleep(RELAY_DELAY)
                
                # CMD: Röle kapat
                ep.write(relay_commands[1]["off"])
                print(f"✅ MSR Reader röle kapatıldı: {relay_commands[1]['off'].hex()}")
                return True
                
            except usb.core.USBError as e:
                if e.errno == 16:
                    print("❌ Cihaz meşgul. Çözüm önerileri:")
                    print("   1. lsusb ile cihazı kontrol edin")
                    print("   2. sudo rmmod usbserial")
                    print("   3. Cihazı çıkarıp tekrar takın")
                elif e.errno == 13:
                    print("❌ Yetki hatası: USB cihazına erişim reddedildi")
                    if not check_udev_rules():
                        print("💡 Yukarıdaki adımları uygulayın ve tekrar deneyin")
                else:
                    print(f"❌ MSR USB hatası: {e}")
                return False
            
    except Exception as e:
        print(f"❌ {device_type} röle kontrolünde hata: {e}")
        return False

def find_usb_devices(device_list):
    found_devices = {}
    
    for device_name, (vendor_id, product_id) in device_list.items():
        # Tüm eşleşen cihazları bul
        devices = list(usb.core.find(find_all=True, idVendor=vendor_id, idProduct=product_id))
        
        if devices:
            if len(devices) == 1:
                found_devices[device_name] = devices[0]
                print(f"🔍 Bulundu: {device_name}")
            else:
                # Birden fazla aynı cihaz varsa, hepsini listele
                found_devices[device_name] = devices
                print(f"🔍 Bulundu {len(devices)} adet {device_name}")
                for i, dev in enumerate(devices, 1):
                    print(f"   {device_name}_{i}: {dev}")
        else:
            print(f"❓ {device_name} bulunamadı")
            
    return found_devices

def main():
    print("🚀 USB Röle Kontrol Sistemi")
    print("=" * 40)
    
    # Udev kurallarını kontrol et
    print("🔧 Sistem kontrolü yapılıyor...")
    check_udev_rules()
    
    # Hedef cihazlar
    target_devices = {
        "MSR_Reader": (0x5131, 0x2007),
        "CH340_Converter": (0x1a86, 0x7523),
    }
    
    print("\n🔍 USB cihazları taranıyor...")
    found_usb_devices = find_usb_devices(target_devices)
    
    if not found_usb_devices:
        print("\n❌ Hiçbir röle cihazı bulunamadı!")
        print("💡 Cihazları kontrol edin:")
        print("   - USB bağlantısını kontrol edin")
        print("   - lsusb komutuyla cihazları listeleyin")
        return
    
    print(f"\n✅ {len(found_usb_devices)} cihaz bulundu. Röle kontrolü başlatılıyor...\n")
    
    # Bulunan cihazları kontrol et
    success_count = 0
    for device_name, device in found_usb_devices.items():
        print(f"🎯 {device_name} kontrol ediliyor...")
        
        if device_name == "MSR_Reader":
            if control_relay_device(device, RelayCommands.RELAY_COMMANDS, device_type="MSR"):
                success_count += 1
                
        elif device_name == "CH340_Converter":
            if control_relay_device(device, RelayCommands.RELAY_COMMANDS, device_type="CH340"):
                success_count += 1
        
        print()  # Boş satır
    
    print("=" * 40)
    print(f"🎉 İşlem tamamlandı: {success_count}/{len(found_usb_devices)} cihaz başarılı")

if __name__ == "__main__":
    main()