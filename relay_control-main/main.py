from relay_control import RelayControl

def main():
    # main-relay Example
    relay_control = RelayControl('main-relay')
    relay_control.trigger_relay('10.10.10.180', 9747)

if __name__ == "__main__":
    main()