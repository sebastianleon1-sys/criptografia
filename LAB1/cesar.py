import sys

texto = sys.argv[1]
desplazamiento = int(sys.argv[2])

cifrado = ""
for char in texto:
    if char.isalpha():
        base = ord('A') if char.isupper() else ord('a')
        cifrado += chr((ord(char) - base + desplazamiento) % 26 + base)
    else:
        cifrado += char

print(cifrado)