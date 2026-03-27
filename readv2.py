from scapy.all import sniff, ICMP
import os, threading

GREEN = "\033[92m"
RESET = "\033[0m"

PALABRAS = {"hola", "el", "la", "de", "que", "en", "un", "es", "con",
            "los", "las", "una", "como", "para", "wireshark", "mensaje"}

def cesar(texto, d):
    out = ""
    for c in texto:
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            out += chr((ord(c) - base - d) % 26 + base)
        else:
            out += c
    return out

def puntaje(texto):
    return sum(1 for p in texto.lower().split() if p in PALABRAS)

def mostrar_resultados(texto):
    os.system("clear")
    print(f"Mensaje capturado: {repr(texto)}\n")
    resultados = [(d, cesar(texto, d)) for d in range(26)]
    mejor = max(resultados, key=lambda x: puntaje(x[1]))
    for d, desc in resultados:
        linea = f"  [{d:02d}] {desc}"
        if d == mejor[0] and puntaje(mejor[1]) > 0:
            print(GREEN + linea + "  ← más probable" + RESET)
        else:
            print(linea)
    print(f"\n{GREEN}Más probable → desplazamiento {mejor[0]}: {mejor[1]}{RESET}")

buffer = []
vistos = set()
timer = None

def reiniciar_timer():
    global timer
    if timer:
        timer.cancel()
    timer = threading.Timer(1.0, timeout)
    timer.start()

def timeout():
    if buffer:
        texto = "".join(buffer)
        buffer.clear()
        vistos.clear()
        mostrar_resultados(texto)

def procesar(pkt):
    if not pkt.haslayer(ICMP):
        return
    # Solo Echo Request (type 8), ignorar Reply (type 0)
    if pkt[ICMP].type != 8:
        return

    icmp = pkt[ICMP]
    seq = icmp.seq

    # Ignorar seq duplicado
    if seq in vistos:
        return
    vistos.add(seq)

    payload = bytes(icmp.payload)
    if not payload:
        return

    char = chr(payload[0])
    buffer.append(char)
    print(f"  Recibido: {''.join(buffer)}", end="\r")
    reiniciar_timer()

print("[*] Escuchando paquetes ICMP... (Ctrl+C para salir)\n")
sniff(filter="icmp and icmp[0]==8", iface="lo", prn=procesar, store=False)