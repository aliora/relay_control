import usb.core
import usb.util
import time

# MSR röle kontrol modeli

class MSRRelay:
    RELAY_COMMANDS = {
        1: {"on": b'\xA0\x01\x01\xA2', "off": b'\xA0\x01\x00\xA1'}
    }
    RELAY_DELAY = 1

    @staticmethod
    def find_devices():
        return list(usb.core.find(find_all=True, idVendor=0x5131, idProduct=0x2007))

    @classmethod
    def trigger(cls, relay_number=1, device_index=0):
        devices = cls.find_devices()
        if device_index >= len(devices):
            print(f"MSR cihaz index {device_index} bulunamadı.")
            return False
        dev = devices[device_index]
        print(f"MSR Reader seçildi: Bus {dev.bus:03d} Device {dev.address:03d}")
        try:
            dev.reset()
            for interface in [0, 1]:
                if dev.is_kernel_driver_active(interface):
                    dev.detach_kernel_driver(interface)
            dev.set_configuration()
            usb.util.claim_interface(dev, 0)
            cfg = dev.get_active_configuration()
            intf = cfg[(0,0)]
            ep = usb.util.find_descriptor(
                intf,
                custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
            )
            if ep is None:
                raise RuntimeError('MSR Endpoint bulunamadı')
            ep.write(cls.RELAY_COMMANDS[relay_number]["on"])
            print(f"MSR röle açıldı: {cls.RELAY_COMMANDS[relay_number]['on'].hex()}")
            time.sleep(cls.RELAY_DELAY)
            ep.write(cls.RELAY_COMMANDS[relay_number]["off"])
            print(f"MSR röle kapatıldı: {cls.RELAY_COMMANDS[relay_number]['off'].hex()}")
            return True
        except Exception as e:
            print(f"MSR röle kontrolünde hata: {e}")
            return False
