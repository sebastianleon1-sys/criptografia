from scapy.all import IP, ICMP, send
import os, time, sys

def send_chars_icmp(message: str, target: str = "127.0.0.1", delay: float = 0.5):
    pid = os.getpid() & 0xFFFF

    print(f"[*] Enviando {len(message)} paquetes ICMP a {target}")
    print(f"[*] PID (ICMP id): {pid}")
    print(f"[*] Mensaje: {repr(message)}\n")

    # Padding igual al ping real de Linux (bytes 0x08 a 0x37)
    padding = bytes(range(0x08, 0x38))

    for seq, char in enumerate(message, start=1):
        pkt = IP(dst=target) / ICMP(type=8, id=pid, seq=seq) / (char.encode() + padding)
        send(pkt, verbose=False)
        print(f"  seq={seq:03d}  char={repr(char)}  hex=0x{ord(char):02X}")
        time.sleep(delay)

    # Enviar 'b' al final como marcador de fin
    seq_final = len(message) + 1
    pkt_fin = IP(dst=target) / ICMP(type=8, id=pid, seq=seq_final) / (b'b' + padding)
    send(pkt_fin, verbose=False)
    print(f"  seq={seq_final:03d}  char='b'  hex=0x{ord('b'):02X}  <-- fin")

    print(f"\n[+] Listo. Filtra en Wireshark con:  icmp")

if __name__ == "__main__":
    mensaje = sys.argv[1] if len(sys.argv) > 1 else "Hola Wireshark"
    send_chars_icmp(mensaje)