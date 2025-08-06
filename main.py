from relay_control import RelayControl


def main():
    # Rn-62 Example
    print("=== RN-62 Röle Testi ===")
    relay_control = RelayControl('rn-62')
    relay_control.trigger_relay('10.10.10.180', 9747, relay_number=1)

    # Rl-02 Example
    print("\n=== RL-02 Röle Testi ===")
    relay_control = RelayControl('rl-02')
    relay_control.trigger_relay('127.0.0.1', 5050, relay_number=3, duration=100)

    # USB Relay Example
    print("\n=== USB Röle Testi ===")
    relay_control = RelayControl('usb-relay')
    # USB röle için IP/port parametreleri kullanılmaz
    relay_control.trigger_relay('', 0, relay_number=1, duration=1000)

    # Jetson Embed Example
    print("\n=== Jetson Embed Röle Testi ===")
    relay_control = RelayControl('jetson-embed')
    relay_control.trigger_relay('127.0.0.1', 9747, relay_number=1)

    # Raspberry Embed Example
    print("\n=== Raspberry Embed Röle Testi ===")
    relay_control = RelayControl('raspberry-embed')
    relay_control.trigger_relay('127.0.0.1', 9747, relay_number=2)

    # Desktop Embed Example
    print("\n=== Desktop Embed Röle Testi ===")
    relay_control = RelayControl('desktop-embed')
    relay_control.trigger_relay('127.0.0.1', 9747, relay_number=1)


def test_all_relays():
    """Tüm röle tiplerini test et"""
    relay_types = {
        'usb-relay': ('', 0),
        'rl-02': ('127.0.0.1', 5050),
        'rn-62': ('10.10.10.180', 9747),
        'jetson-embed': ('127.0.0.1', 9747),
        'raspberry-embed': ('127.0.0.1', 9747),
        'desktop-embed': ('127.0.0.1', 9747)
    }
    
    for relay_type, (ip, port) in relay_types.items():
        try:
            print(f"\n=== {relay_type.upper()} Test ===")
            relay_control = RelayControl(relay_type)
            success = relay_control.trigger_relay(ip, port, relay_number=1, duration=500)
            print(f"{relay_type} sonuç: {'BAŞARILI' if success else 'BAŞARISIZ'}")
        except Exception as e:
            print(f"{relay_type} hatası: {e}")


if __name__ == "__main__":
    # main()  # Temel örnekler
    test_all_relays()  # Tüm röle tiplerini test et