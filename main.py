from relay_control import RelayControl


def main():
    # CH340 Converter Example  
    try:
        ch340_relay = RelayControl('ch340-converter')
        ch340_relay.trigger_relay(duration=3)
        print("CH340 Converter röle başarıyla tetiklendi")
    except Exception as e:
        print(f"CH340 Converter hatası: {e}")

    # Rn-62 Example (mevcut)
    try:
        rn62_relay = RelayControl('rn-62')
        rn62_relay.trigger_relay('10.10.10.180', 9747, relay_number=1)
        print("RN-62 röle başarıyla tetiklendi")
    except Exception as e:
        print(f"RN-62 hatası: {e}")


if __name__ == "__main__":
    main()
