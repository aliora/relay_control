import usb.core
import usb.util
import serial
import serial.tools.list_ports
import time
import socket


class USBRelayIO:
    """USB Relay IO sınıfı - MSR Reader ve CH340 Converter desteği"""
    
    RELAY_DELAY = 1  # seconds
    
    RELAY_COMMANDS = {
        1: {"on": b'\xA0\x01\x01\xA2', "off": b'\xA0\x01\x00\xA1'}
    }
    
    TARGET_DEVICES = {
        "MSR_Reader": (0x5131, 0x2007),
        "CH340_Converter": (0x1a86, 0x7523),
    }

    def trigger_relays(self, ip, port, relay_number=None, duration=None):
        """Ana röle tetik fonksiyonu - diğer model sınıflarıyla uyumlu"""
        try:
            # Duration parametresi varsa kullan, yoksa varsayılan değeri al
            if duration:
                self.RELAY_DELAY = duration / 1000  # millisaniye'den saniyeye çevir
            
            print("USB cihazları taranıyor...")
            found_devices = self._find_usb_devices()
            print("Tarama tamamlandı.")
            
            success = False
            
            # Bulunan cihazları kontrol et
            for device_name, device in found_devices.items():
                if device_name == "MSR_Reader":
                    print("MSR Reader bulundu, tetikleniyor...")
                    if self._control_relay_device(device, device_type="MSR"):
                        success = True
                        
                elif device_name == "CH340_Converter":
                    print("CH340 Converter bulundu, tetikleniyor...")
                    if self._control_relay_device(device, device_type="CH340"):
                        success = True
            
            # Hiçbir cihaz bulunamazsa uyarı
            if not found_devices:
                print("Hiçbir USB röle cihazı bulunamadı")
                return False
                
            return success
            
        except Exception as e:
            print(f"USB Relay tetikleme hatası: {e}")
            return False

    def _find_usb_devices(self):
        """USB cihazlarını tarar ve bulur"""
        found_devices = {}
        
        for device_name, (vendor_id, product_id) in self.TARGET_DEVICES.items():
            # Tüm eşleşen cihazları bul
            devices = list(usb.core.find(find_all=True, idVendor=vendor_id, idProduct=product_id))
            
            if devices:
                if len(devices) == 1:
                    found_devices[device_name] = devices[0]
                else:
                    # Birden fazla aynı cihaz varsa, ilkini al
                    found_devices[device_name] = devices[0]
                    print(f"Bulundu {len(devices)} adet {device_name}, ilki kullanılıyor")
                    
        return found_devices

    def _control_relay_device(self, device, device_type="CH340"):
        """Cihaz tipine göre röle kontrolü yapar"""
        try:
            if device_type == "CH340":
                return self._control_ch340_relay(device)
            elif device_type == "MSR":
                return self._control_msr_relay(device)
            else:
                print(f"Desteklenmeyen cihaz tipi: {device_type}")
                return False
                
        except Exception as e:
            print(f"{device_type} röle kontrolünde hata: {e}")
            return False

    def _control_ch340_relay(self, device):
        """CH340 Converter röle kontrolü"""
        try:
            # Port arama
            ports = serial.tools.list_ports.comports()
            target_port = None
            
            # VID/PID kontrol
            for port in ports:
                if port.vid == 0x1a86 and port.pid == 0x7523:
                    target_port = port.device
                    break
            
            # Port bulunamadı
            if target_port is None:
                print("CH340 seri portu bulunamadı")
                return False
                
            # Seri port bağlantısı
            with serial.Serial(target_port, baudrate=9600, timeout=1) as ser:
                # Röle aç
                ser.write(self.RELAY_COMMANDS[1]["on"])
                print(f"CH340 Converter röle açıldı: {self.RELAY_COMMANDS[1]['on'].hex()}")
                
                # Bekle
                print(f"Röle {self.RELAY_DELAY} saniye açık kalacak...")
                time.sleep(self.RELAY_DELAY)
                
                # Röle kapat
                ser.write(self.RELAY_COMMANDS[1]["off"])
                print(f"CH340 Converter röle kapatıldı: {self.RELAY_COMMANDS[1]['off'].hex()}")
                return True
                
        except Exception as e:
            print(f"CH340 kontrolünde hata: {e}")
            return False

    def _control_msr_relay(self, device):
        """MSR Reader röle kontrolü"""
        try:
            # USB reset
            device.reset()
            
            # Driver ayarları
            for interface in [0, 1]:
                if device.is_kernel_driver_active(interface):
                    device.detach_kernel_driver(interface)
            
            # USB ayarları
            device.set_configuration()
            usb.util.claim_interface(device, 0)
            
            # Endpoint bulma
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
            
            # Röle aç
            ep.write(self.RELAY_COMMANDS[1]["on"])
            print(f"MSR Reader röle açıldı: {self.RELAY_COMMANDS[1]['on'].hex()}")
            
            # Bekle
            print(f"Röle {self.RELAY_DELAY} saniye açık kalacak...")
            time.sleep(self.RELAY_DELAY)
            
            # Röle kapat
            ep.write(self.RELAY_COMMANDS[1]["off"])
            print(f"MSR Reader röle kapatıldı: {self.RELAY_COMMANDS[1]['off'].hex()}")
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
            print(f"MSR kontrolünde hata: {e}")
            return False