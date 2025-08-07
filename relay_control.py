import os
import sys

# Mevcut dizini Python path'e ekle
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Models klasörünü de ekle
models_path = os.path.join(current_dir, 'models')
if models_path not in sys.path:
    sys.path.insert(0, models_path)

# Import'ları dene
try:
    # Önce doğrudan models klasöründen import dene
    from Rl02_IO import Rl02IO
    from Rn62_IO import Rn62IO
    from Jetson_Embed import JetsonEmbed
    from Raspberry_Embed import RaspberryEmbed
    from Desktop_Embed import DesktopEmbed
    from USB_Relay_IO import USBRelayIO
except ImportError:
    # Relative import dene
    from models.Rl02_IO import Rl02IO
    from models.Rn62_IO import Rn62IO
    from models.Jetson_Embed import JetsonEmbed
    from models.Raspberry_Embed import RaspberryEmbed
    from models.Desktop_Embed import DesktopEmbed
    from models.USB_Relay_IO import USBRelayIO


class RelayControl:
    """
    Relay Control sınıfı - Çeşitli röle tiplerini destekler
    
    Desteklenen markalar:
    - rl-02: Isbitek RL-02 IO kartı
    - rn-62: Runitek RN-62 IO kartı  
    - jetson-embed: Jetson embedded sistem
    - raspberry-embed: Raspberry Pi embedded sistem
    - desktop-embed: Desktop embedded sistem
    - usb-relay: USB röle modülleri (MSR Reader, CH340)
    """
    
    def __init__(self, brand):
        self.brand = brand.lower()
        self._initialize_relay_instance()

    def _initialize_relay_instance(self):
        """Marka tipine göre ilgili röle instance'ını oluşturur"""
        if self.brand == 'rl-02':
            self.relay_instance = Rl02IO()
        elif self.brand == 'rn-62':
            self.relay_instance = Rn62IO()
        elif self.brand == 'jetson-embed':
            self.relay_instance = JetsonEmbed()
        elif self.brand == 'raspberry-embed':
            self.relay_instance = RaspberryEmbed()
        elif self.brand == 'desktop-embed':
            self.relay_instance = DesktopEmbed()
        elif self.brand == 'usb-relay':
            self.relay_instance = USBRelayIO()
        else:
            supported_brands = self.get_supported_brands()
            raise ValueError(f"Desteklenmeyen röle markası: {self.brand}. Desteklenenler: {supported_brands}")

    def trigger_relay(self, ip, port, relay_number=None, duration=100):
        """
        Röle tetikleme fonksiyonu
        
        Args:
            ip (str): Hedef IP adresi
            port (int): Hedef port
            relay_number (int, optional): Röle numarası. None ise tüm röleleri tetikler
            duration (int): Tetikleme süresi (ms)
        
        Returns:
            bool: İşlem başarılı ise True
        """
        return self.relay_instance.trigger_relays(ip, port, relay_number, duration)
    
    def get_supported_brands(self):
        """Desteklenen röle markalarını döndürür"""
        return ['rl-02', 'rn-62', 'jetson-embed', 'raspberry-embed', 'desktop-embed', 'usb-relay']
    
    def get_brand(self):
        """Mevcut marka tipini döndürür"""
        return self.brand
    
    def __str__(self):
        return f"RelayControl({self.brand})"
    
    def __repr__(self):
        return f"RelayControl(brand='{self.brand}')"