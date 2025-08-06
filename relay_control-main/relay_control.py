from .models.Main_relay import RelayControl as MainRelayControl
from .models.Jetson_Embed import JetsonEmbed
from .models.Raspberry_Embed import RaspberryEmbed
from .models.Desktop_Embed import DesktopEmbed


class RelayControl:
    def __init__(self, brand):
        self.brand = brand

        if self.brand == 'main-relay':
            self.relay_instance = MainRelayControl()
        elif self.brand == 'jetson-embed':
            self.relay_instance = JetsonEmbed()
        elif self.brand == 'raspberry-embed':
            self.relay_instance = RaspberryEmbed()
        elif self.brand == 'desktop-embed':
            self.relay_instance = DesktopEmbed()
        else:
            raise ValueError("Unsupported brand for relay control")

    def trigger_relay(self, ip, port, relay_number=None, duration=100):
        return self.relay_instance.trigger_relay(ip, port, relay_number, duration)