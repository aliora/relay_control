from relay_control import RelayControl


def main():
    print("=== Relay Control Test Programı ===\n")
    
    # CH340 Converter Test
    print("1. CH340 Converter test ediliyor...")
    try:
        ch340_relay = RelayControl('ch340-converter')
        print("CH340 Converter bulundu!")
        
        # 3 saniye röle tetikle
        result = ch340_relay.trigger_relay(duration=3)
        
        if result:
            print("✓ CH340 Converter röle başarıyla tetiklendi!")
        else:
            print("✗ CH340 Converter röle tetiklenemedi!")
            
    except Exception as e:
        print(f"✗ CH340 Converter hatası: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Mevcut Rn-62 Test (örnek)
    print("2. RN-62 test ediliyor...")
    try:
        rn62_relay = RelayControl('rn-62')
        result = rn62_relay.trigger_relay('10.10.10.180', 9747, relay_number=1, duration=2)
        
        if result:
            print("✓ RN-62 röle başarıyla tetiklendi!")
        else:
            print("✗ RN-62 röle tetiklenemedi!")
            
    except Exception as e:
        print(f"✗ RN-62 hatası: {e}")

    print("\n" + "="*50 + "\n")

    # Mevcut RL-02 Test (örnek)
    print("3. RL-02 test ediliyor...")
    try:
        rl02_relay = RelayControl('rl-02')
        result = rl02_relay.trigger_relay('192.168.1.100', 8080, relay_number=1, duration=2)
        
        if result:
            print("✓ RL-02 röle başarıyla tetiklendi!")
        else:
            print("✗ RL-02 röle tetiklenemedi!")
            
    except Exception as e:
        print(f"✗ RL-02 hatası: {e}")

    print("\nTest tamamlandı!")


if __name__ == "__main__":
    main()
