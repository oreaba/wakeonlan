import socket
import re

def send_wol(mac: str):
    # Clean MAC address (accepts formats: XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX)
    mac = re.sub(r'[^0-9A-Fa-f]', '', mac)
    if len(mac) != 12:
        raise ValueError("Invalid MAC address format")

    # Build magic packet
    mac_bytes = bytes.fromhex(mac)
    magic_packet = b'\xff' * 6 + mac_bytes * 16

    # Send UDP broadcast on port 9
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto(magic_packet, ("255.255.255.255", 9))
