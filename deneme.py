import serial
import time
import serial.tools.list_ports
from typing import Optional

print("Basit USB Röle Kontrol Sistemi yüklendi.")

class SimpleUSBRelay:
    def __init__(self):
        """
        Basit USB Röle Kontrol Sınıfı - Tamamen Local
        Hiçbir yere bağlanmaz, sadece USB röle kartını kontrol eder
        """
        self.port = None
        self.baud_rate = 9600
        self.serial_connection = None
        
        # 3 röle durumu
        self.relay_states = {1: False, 2: False, 3: False}
        
        # Röle bilgileri
        self.relays = {
            1: "Tongling JQC-3FF-S-Z (10A/15A)",
            2: "Generic SRD-5VDC-SL-C (10A)", 
            3: "Songle SRD-5VDC-SL-C (10A)"
        }
        
        print(f"✅ 3 Röle tanımlandı:")
        for num, name in self.relays.items():
            print(f"   Röle {num}: {name}")
    
    def find_usb_port(self):
        """USB röle portunu otomatik bulur"""
        print("🔍 USB röle kartı otomatik aranıyor...")
        
        ports = list(serial.tools.list_ports.comports())
        
        if not ports:
            print("❌ Hiçbir USB port bulunamadı!")
            return None
        
        # USB röle kartı belirtileri (daha kapsamlı)
        relay_indicators = {
            "USB": ["USB"], 
            "Serial": ["Serial", "USB-SERIAL", "USB2.0-Serial", "USB-to-Serial"], 
            "Chipset": ["CH340", "CP210", "FTDI", "Prolific", "Silicon Labs", "QinHeng", "WCH"],
            "Device": ["Arduino", "USB-Serial Controller", "USB-UART"] # Genel cihaz açıklamaları
        }
        
        print("📍 Bulunan portlar:")
        potential_ports = []
        
        for port in ports:
            description = (port.description or "").upper()
            manufacturer = (port.manufacturer or "").upper()
            hwid = (port.hwid or "").upper() # Donanım ID'si de kontrol edilebilir
            
            print(f"\n   📌 {port.device}")
            print(f"      Açıklama: {port.description}")
            print(f"      Üretici: {port.manufacturer}")
            print(f"      HWID: {port.hwid}")
            
            # USB-Serial adaptör kontrolü
            is_usb_serial = False
            triggered_by = []

            for category, indicators in relay_indicators.items():
                for indicator in indicators:
                    if indicator in description:
                        is_usb_serial = True
                        triggered_by.append(f"Açıklama: {indicator} ({category})")
                    if indicator in manufacturer:
                        is_usb_serial = True
                        triggered_by.append(f"Üretici: {indicator} ({category})")
                    if indicator in hwid: # HWID kontrolü eklendi
                        is_usb_serial = True
                        triggered_by.append(f"HWID: {indicator} ({category})")
            
            if is_usb_serial:
                print(f"      ✅ USB-Serial adaptör tespit edildi!")
                for trigger in triggered_by:
                    print(f"         • Tetikleyen: {trigger}")
                potential_ports.append(port.device)
            else:
                print(f"      ⚪ Standart port (Röle kartı belirtisi bulunamadı)")
            
            print("   " + "-"*40)
        
        # En uygun portu seç
        if potential_ports:
            selected_port = potential_ports[0]
            print(f"\n🎯 USB röle portu seçildi: {selected_port}")
            if len(potential_ports) > 1:
                print(f"ℹ️  Diğer potansiyel portlar: {potential_ports[1:]}")
            return selected_port
        
        # USB-Serial bulunamazsa ilk portu dene
        if ports:
            selected_port = ports[0].device
            print(f"\n⚠️  USB-Serial belirtisi bulunamadı, ilk port deneniyor: {selected_port}")
            return selected_port
        
        return None
    
    def connect(self):
        """USB röle kartına otomatik bağlan"""
        if not self.port:
            print("🔄 Bağlantı için önce port bulunuyor...")
            self.port = self.find_usb_port()
            
        if not self.port:
            print("❌ USB röle kartı bulunamadı veya seçilemedi!")
            return False
            
        # Yaygın baud rate'leri dene
        baud_rates = [9600, 19200, 38400, 57600, 115200]
        
        print(f"\n🔌 {self.port} portuna bağlanmaya çalışılıyor...")
        
        for baud in baud_rates:
            try:
                print(f"   ⚡ {baud} baud deneniyor...")
                
                self.serial_connection = serial.Serial(
                    port=self.port,
                    baudrate=baud,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=1,
                    write_timeout=1
                )
                
                time.sleep(0.5)  # Bağlantının oturması için bekle
                
                if self.serial_connection.is_open:
                    self.baud_rate = baud
                    print(f"   ✅ Bağlantı {self.port} @ {baud} baud ile başarılı.")
                    
                    # Test komutu gönder
                    print("   🧪 Bağlantı testi yapılıyor (Röle 1 açma komutu gönderiliyor)...")
                    test_success = self.test_connection()
                    if test_success:
                        print("   🎯 Röle kartı yanıt veriyor gibi görünüyor!")
                        return True
                    else:
                        print("   ⚠️  Port açık ama röle kartı yanıt vermedi. Yine de devam ediliyor...")
                        return True  # Yine de devam et, bazı kartlar yanıt göndermeyebilir
                        
            except serial.SerialException as se:
                print(f"   ❌ {baud} baud ile seri port hatası: {se}")
                if self.serial_connection:
                    try:
                        self.serial_connection.close()
                    except:
                        pass
                continue
            except Exception as e:
                print(f"   ❌ {baud} baud ile beklenmeyen hata: {e}")
                if self.serial_connection:
                    try:
                        self.serial_connection.close()
                    except:
                        pass
                continue
                
        print("❌ Hiçbir konfigürasyonla bağlanılamadı!")
        return False
    
    def test_connection(self):
        """Bağlantıyı test et"""
        if not self.serial_connection or not self.serial_connection.is_open:
            print("   ⚠️  Bağlantı açık değil, test edilemiyor.")
            return False
            
        try:
            # Basit test komutu gönder (Röle 1'i açma)
            test_command = b'\xA0\x01\x01\xA2'
            print(f"   📤 Test komutu gönderiliyor: {test_command.hex()}")
            self.serial_connection.write(test_command)
            self.serial_connection.flush()
            time.sleep(0.2)
            
            # Yanıt varsa oku
            if self.serial_connection.in_waiting > 0:
                response = self.serial_connection.read(self.serial_connection.in_waiting)
                print(f"   📥 Test yanıtı alındı: {response.hex()} ({len(response)} byte)")
                return True
            else:
                print("   🚫 Test komutuna yanıt alınamadı. (Bazı kartlar yanıt vermez)")
                return True # Yanıt olmasa da bağlantı var sayılabilir
            
        except Exception as e:
            print(f"   ❌ Bağlantı testi başarısız: {e}")
            return False
    
    def send_command(self, command_bytes):
        """Röle kartına komut gönder"""
        if not self.serial_connection or not self.serial_connection.is_open:
            print("❌ Bağlantı yok veya açık değil! Komut gönderilemiyor.")
            return False
            
        try:
            print(f"   [DEBUG] Gönderilen komut: {command_bytes.hex()}")
            self.serial_connection.write(command_bytes)
            time.sleep(0.1)
            return True
        except serial.SerialException as se:
            print(f"❌ Komut gönderme hatası (Seri Port): {se}")
            return False
        except Exception as e:
            print(f"❌ Komut gönderme hatası (Genel): {e}")
            return False
    
    def test_commands(self):
        """Farklı komut türlerini test et"""
        print("\n🧪 Komut testi başlıyor...")
        print("Röle sesini dinleyin ve çalışan komutu seçin!")
        
        # Test komutları
        test_sets = {
            "1": {
                "name": "Basit Hex Komutlar (A0 0x 0x Ax)",
                1: {"on": b'\xA0\x01\x01\xA2', "off": b'\xA0\x01\x00\xA1'}
            },
            "2": {
                "name": "ASCII Komutlar (örn: '11', '10')", 
                1: {"on": b'11', "off": b'10'}
            },
            "3": {
                "name": "Hex String Komutlar (örn: 'A00101A1')",
                1: {"on": b'A00101A1', "off": b'A00100A0'}
            },
            "4": {
                "name": "CRLF Komutlar (örn: 'A005\\r\\n')",
                1: {"on": b'A005\r\n', "off": b'A006\r\n'}
            }
        }
        
        for set_id, command_set in test_sets.items():
            print(f"\n--- {command_set['name']} Test ---")
            
            # Açma komutu
            print(f"📤 Röle 1 AÇMA komutu gönderiliyor: {command_set[1]['on'].hex() if isinstance(command_set[1]['on'], bytes) else command_set[1]['on']}")
            self.send_command(command_set[1]["on"])
            time.sleep(1)
            
            # Kapatma komutu  
            print(f"📤 Röle 1 KAPAMA komutu gönderiliyor: {command_set[1]['off'].hex() if isinstance(command_set[1]['off'], bytes) else command_set[1]['off']}")
            self.send_command(command_set[1]["off"])
            time.sleep(1)
            
            response = input("Bu komutlar çalıştı mı? (y/n): ").lower()
            if response in ['y', 'yes', 'evet']:
                print(f"✅ {command_set['name']} seçildi!")
                # Burada seçilen komut setini kaydedebilirsiniz, ancak mevcut kodda bu kısım kullanılmıyor.
                # Örneğin: self.active_command_set = set_id
                return set_id
                
        print("❌ Hiçbir komut çalışmadı")
        return "1"  # Varsayılan
    
    def control_relay(self, relay_num, state):
        """Röle kontrol et"""
        if relay_num not in [1, 2, 3]:
            print(f"❌ Geçersiz röle: {relay_num}. Sadece 1, 2 veya 3 olabilir.")
            return False
            
        # Basit hex komutlar (en yaygın)
        commands = {
            1: {"on": b'\xA0\x01\x01\xA2', "off": b'\xA0\x01\x00\xA1'},
            2: {"on": b'\xA0\x02\x01\xA3', "off": b'\xA0\x02\x00\xA2'}, 
            3: {"on": b'\xA0\x03\x01\xA4', "off": b'\xA0\x03\x00\xA3'}
        }
        
        action = "AÇILIYOR" if state else "KAPATILIYOR"
        relay_name = self.relays[relay_num]
        
        print(f"🔧 Röle {relay_num} ({relay_name}) {action}...")
        
        command = commands[relay_num]["on"] if state else commands[relay_num]["off"]
        success = self.send_command(command)
        
        if success:
            self.relay_states[relay_num] = state
            status = "AÇIK" if state else "KAPALI"
            print(f"✅ Röle {relay_num} şimdi {status}.")
        else:
            print(f"❌ Röle {relay_num} kontrolü başarısız.")
        
        return success
    
    def open_relay(self, relay_num):
        """Röle aç"""
        return self.control_relay(relay_num, True)
    
    def close_relay(self, relay_num):
        """Röle kapat"""
        return self.control_relay(relay_num, False)
    
    def open_all(self):
        """Tüm röleleri aç"""
        print("🔄 Tüm röleler açılıyor...")
        for i in [1, 2, 3]:
            self.open_relay(i)
            time.sleep(0.2)
    
    def close_all(self):
        """Tüm röleleri kapat"""
        print("🔄 Tüm röleler kapatılıyor...")
        for i in [1, 2, 3]:
            self.close_relay(i)
            time.sleep(0.2)
    
    def test_all(self):
        """Tüm röleleri test et"""
        print("🧪 Tüm röleler test ediliyor...")
        
        for relay_num in [1, 2, 3]:
            print(f"\n--- Röle {relay_num} Test ---")
            self.open_relay(relay_num)
            time.sleep(2)
            self.close_relay(relay_num)
            time.sleep(1)
            
        print("✅ Tüm röle testi tamamlandı!")
    
    def show_status(self):
        """Röle durumlarını göster"""
        print("\n" + "="*40)
        print("📊 RÖLE DURUMLARI")
        print("="*40)
        
        for relay_num in [1, 2, 3]:
            state = self.relay_states[relay_num]
            status = "🟢 AÇIK" if state else "🔴 KAPALI"
            name = self.relays[relay_num]
            print(f"Röle {relay_num}: {status} - {name}")
        
        print("="*40)
    
    def menu(self):
        """Basit kontrol menüsü"""
        while True:
            print("\n" + "="*40)
            print("🎮 USB RÖLE KONTROL")
            print("="*40)
            print("1. Röle 1 Aç")
            print("2. Röle 1 Kapat")
            print("3. Röle 2 Aç") 
            print("4. Röle 2 Kapat")
            print("5. Röle 3 Aç")
            print("6. Röle 3 Kapat")
            print("7. Tümünü Aç")
            print("8. Tümünü Kapat")
            print("9. Test Et")
            print("s. Durum Göster")
            print("0. Çıkış")
            
            choice = input("\nSeçiminiz: ").strip().lower()
            
            if choice == '1':
                self.open_relay(1)
            elif choice == '2':
                self.close_relay(1)
            elif choice == '3':
                self.open_relay(2)
            elif choice == '4':
                self.close_relay(2)
            elif choice == '5':
                self.open_relay(3)
            elif choice == '6':
                self.close_relay(3)
            elif choice == '7':
                self.open_all()
            elif choice == '8':
                self.close_all()
            elif choice == '9':
                self.test_all()
            elif choice == 's':
                self.show_status()
            elif choice == '0':
                print("👋 Çıkış...")
                break
            else:
                print("❌ Geçersiz seçim!")
    
    def manual_port_selection(self):
        """Manuel port seçimi"""
        ports = list(serial.tools.list_ports.comports())
        
        if not ports:
            print("❌ Hiçbir port bulunamadı!")
            return
            
        print("\n📍 Mevcut tüm portlar:")
        for i, port in enumerate(ports):
            print(f"   {i+1}. {port.device} - {port.description} (Üretici: {port.manufacturer or 'Yok'}, HWID: {port.hwid or 'Yok'})")
            
        try:
            choice = input(f"\nHangi portu denemek istersiniz? (1-{len(ports)} veya 'q' iptal için): ").strip().lower()
            if choice == 'q':
                print("Manuel seçim iptal edildi.")
                return False
            
            port_index = int(choice) - 1
            
            if 0 <= port_index < len(ports):
                self.port = ports[port_index].device
                print(f"✅ Manuel seçim: {self.port}")
                return True
            else:
                print("❌ Geçersiz seçim!")
                return False
                
        except ValueError:
            print("❌ Geçersiz giriş! Lütfen bir sayı girin.")
            return False
    
    def quick_test(self):
        """Hızlı röle testi"""
        print("⚡ Her röle 1 saniye açılıp kapatılacak...")
        
        for relay_num in [1, 2, 3]:
            print(f"   🔧 Röle {relay_num} test ediliyor...")
            self.open_relay(relay_num)
            time.sleep(1)
            self.close_relay(relay_num)
            time.sleep(0.5)
            
    def disconnect(self):
        """Bağlantıyı kapat"""
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.close()
                print("🔌 Bağlantı kapatıldı.")
            except Exception as e:
                print(f"❌ Bağlantı kapatılırken hata oluştu: {e}")
        else:
            print("ℹ️  Bağlantı zaten kapalıydı.")

# Ana program - Tamamen Otomatik
def main():
    print("🚀 Otomatik USB Röle Kontrol - Tamamen Local")
    print("=" * 50)
    print("ℹ️  Bu program hiçbir yere bağlanmaz!")
    print("ℹ️  USB röle kartını otomatik bulur ve bağlanır")
    print("=" * 50)
    
    # Röle controller başlat
    relay = SimpleUSBRelay()
    
    try:
        # USB porta otomatik bağlan
        print("\n🔍 USB röle kartı aranıyor ve bağlanıyor...")
        
        connected = relay.connect()

        if not connected:
            print("\n❌ USB röle kartına otomatik bağlanılamadı!")
            print("\n🔧 Kontrol edilecekler:")
            print("   • USB röle kartı bağlı mı?")
            print("   • USB kablosu çalışıyor mu?")  
            print("   • Röle kartı açık mı?")
            print("   • Driver kurulu mu? (Windows için)")
            print("   • Port izinleri uygun mu? (Linux için)")
            
            # Manual port seçimi öner
            choice = input("\nManual port seçimi yapmak ister misiniz? (y/n): ")
            if choice.lower() in ['y', 'yes', 'evet']:
                if relay.manual_port_selection(): # Manuel seçim başarılıysa tekrar dene
                    connected = relay.connect()
                else:
                    print("Manuel seçimden vazgeçildi veya geçersizdi. Program sonlanıyor.")
                    return
            else:
                print("Program sonlanıyor.")
                return
        
        if connected:
            print("\n✅ USB röle kartı bulundu ve bağlandı!")
            
            # Hızlı test öner
            test_choice = input("\nHızlı röle testi yapmak ister misiniz? (y/n): ").lower()
            if test_choice in ['y', 'yes', 'evet', '']:
                print("\n🧪 Hızlı test başlıyor...")
                relay.quick_test()
            
            # Ana menüyü başlat
            print("\n🎮 Ana kontrol menüsü başlıyor...")
            relay.menu()
        else:
            print("\n❌ USB röle kartına bağlanılamadı. Lütfen sorunları kontrol edin ve tekrar deneyin.")

    except KeyboardInterrupt:
        print("\n👋 Program kullanıcı tarafından sonlandırıldı (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Beklenmeyen bir hata oluştu: {e}")
    finally:
        # Güvenlik için tüm röleleri kapat
        print("\n🔒 Güvenlik için tüm röleler kapatılıyor...")
        try:
            relay.close_all()
            time.sleep(0.5)
        except Exception as e:
            print(f"⚠️  Tüm röleleri kapatırken hata: {e}")
        relay.disconnect()
        print("✅ Program güvenli şekilde sonlandırıldı.")

if __name__ == "__main__":
    main()