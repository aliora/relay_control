from .models.Rl02_IO import Rl02IO
from .models.Rn62_IO import Rn62IO
from .models.Jetson_Embed import JetsonEmbed
from .models.Raspberry_Embed import RaspberryEmbed
from .models.Desktop_Embed import DesktopEmbed
from .models.CH340_Converter import CH340Converter


class RelayControl:
    def __init__(self, brand):
        self.brand = brand

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
        elif self.brand == 'ch340-converter':
            self.relay_instance = CH340Converter()
        else:
            raise ValueError(f"Unsupported brand for relay control: {self.brand}")

    def trigger_relay(self, ip=None, port=None, relay_number=1, duration=3):
        """
        Unified interface for all relay types
        """
        # CH340 için IP/port gerekmez, sadece relay_number ve duration
        if self.brand == 'ch340-converter':
            return self.relay_instance.trigger_relays(
                relay_number=relay_number, 
                duration=duration
            )
        # Embedded sistemler (Raspberry, Jetson, Desktop) için sadece relay_number ve duration
        elif self.brand in ['raspberry-embed', 'jetson-embed', 'desktop-embed']:
            return self.relay_instance.trigger_relays(
                relay_number=relay_number, 
                duration=duration
            )
        # Network tabanlı röle sistemleri (RL-02, RN-62) için IP ve port gerekli
        else:
            return self.relay_instance.trigger_relays(ip, port, relay_number, duration)
