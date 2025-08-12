from models.CH340Relay import CH340Relay
from models.MSRRelay import MSRRelay

def trigger_specific_relay(relay_number):
    # Cihazları sırayla bul ve tetikle
    msr_devices = MSRRelay.find_devices()
    ch340_ports = CH340Relay.find_ports()
    device_mapping = []
    for i in range(len(msr_devices)):
        device_mapping.append(('MSR', i))
    for i in range(len(ch340_ports)):
        device_mapping.append(('CH340', i))
    if relay_number < 1 or relay_number > len(device_mapping):
        print(f"Geçersiz relay numarası: {relay_number}")
        return False
    device_type, device_index = device_mapping[relay_number - 1]
    if device_type == 'MSR':
        return MSRRelay.trigger(device_index=device_index)
    elif device_type == 'CH340':
        return CH340Relay.trigger(device_index=device_index)
    return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        try:
            relay_number = int(sys.argv[1])
            trigger_specific_relay(relay_number)
        except Exception as e:
            print(f"Hata: {e}")
    else:
        # Tüm cihazları sırayla tetikle
        msr_devices = MSRRelay.find_devices()
        for i in range(len(msr_devices)):
            MSRRelay.trigger(device_index=i)
        ch340_ports = CH340Relay.find_ports()
        for i in range(len(ch340_ports)):
            CH340Relay.trigger(device_index=i)