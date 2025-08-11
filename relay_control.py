class RelayControl:
    def __init__(self, brand=None):
        self.brand = brand or "CH340"
        self.commands = RelayCommands.RELAY_COMMANDS

    def triggerRelays(self, ip=None, port=None, relayNumber=None, duration=None):
        if relayNumber:
            return trigger_specific_relay(relayNumber)
        else:
            return self.trigger()

    def trigger(self, device_type=None):
        device_type = device_type or self.brand
        target_devices = {
            "MSR_Reader": (0x5131, 0x2007),
            "CH340_Converter": (0x1a86, 0x7523),
        }
        found_devices = find_usb_devices(target_devices)
        if device_type == "MSR" and "MSR_Reader" in found_devices:
            return control_relay_device(found_devices["MSR_Reader"], self.commands, device_type="MSR")
        elif device_type in ["CH340", "MSR-CH340"] and "CH340_Converter" in found_devices:
            return control_relay_device(found_devices["CH340_Converter"], self.commands, device_type="CH340")
        return False
