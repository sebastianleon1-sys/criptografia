from Crypto.Cipher import DES, AES, DES3
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64


def ajustar_bytes(valor_usuario, largo_requerido, nombre):
    datos = valor_usuario.encode("utf-8")

    if len(datos) < largo_requerido:
        faltan = largo_requerido - len(datos)
        datos += get_random_bytes(faltan)
        print(f"{nombre}: era menor. Se agregaron {faltan} bytes aleatorios.")

    elif len(datos) > largo_requerido:
        datos = datos[:largo_requerido]
        print(f"{nombre}: era mayor. Se truncó a {largo_requerido} bytes.")

    else:
        print(f"{nombre}: tamaño correcto.")

    return datos


def imprimir_resultados(algoritmo, key, iv, texto_cifrado, texto_descifrado):
    print("\n" + "=" * 50)
    print(f"RESULTADOS {algoritmo}")
    print("=" * 50)
    print("Key final HEX:", key.hex())
    print("IV final HEX:", iv.hex())
    print("Texto cifrado HEX:", texto_cifrado.hex())
    print("Texto cifrado Base64:", base64.b64encode(texto_cifrado).decode())
    print("Texto descifrado:", texto_descifrado)


def proceso_des(texto, key_usuario, iv_usuario):
    key = ajustar_bytes(key_usuario, 8, "Key DES")
    iv = ajustar_bytes(iv_usuario, 8, "IV DES")

    cipher = DES.new(key, DES.MODE_CBC, iv)
    texto_cifrado = cipher.encrypt(pad(texto.encode("utf-8"), DES.block_size))

    decipher = DES.new(key, DES.MODE_CBC, iv)
    texto_descifrado = unpad(decipher.decrypt(texto_cifrado), DES.block_size).decode("utf-8")

    imprimir_resultados("DES CBC", key, iv, texto_cifrado, texto_descifrado)


def proceso_aes256(texto, key_usuario, iv_usuario):
    key = ajustar_bytes(key_usuario, 32, "Key AES-256")
    iv = ajustar_bytes(iv_usuario, 16, "IV AES-256")

    cipher = AES.new(key, AES.MODE_CBC, iv)
    texto_cifrado = cipher.encrypt(pad(texto.encode("utf-8"), AES.block_size))

    decipher = AES.new(key, AES.MODE_CBC, iv)
    texto_descifrado = unpad(decipher.decrypt(texto_cifrado), AES.block_size).decode("utf-8")

    imprimir_resultados("AES-256 CBC", key, iv, texto_cifrado, texto_descifrado)


def proceso_3des(texto, key_usuario, iv_usuario):
    key = ajustar_bytes(key_usuario, 24, "Key 3DES")

    try:
        key = DES3.adjust_key_parity(key)
    except ValueError:
        print("La key de 3DES no era válida. Se generó una nueva.")
        key = DES3.adjust_key_parity(get_random_bytes(24))

    iv = ajustar_bytes(iv_usuario, 8, "IV 3DES")

    cipher = DES3.new(key, DES3.MODE_CBC, iv)
    texto_cifrado = cipher.encrypt(pad(texto.encode("utf-8"), DES3.block_size))

    decipher = DES3.new(key, DES3.MODE_CBC, iv)
    texto_descifrado = unpad(decipher.decrypt(texto_cifrado), DES3.block_size).decode("utf-8")

    imprimir_resultados("3DES CBC", key, iv, texto_cifrado, texto_descifrado)


def main():
    print("LABORATORIO 4 - CIFRADO SIMETRICO")
    print("DES, AES-256 y 3DES en modo CBC\n")

    texto = input("Ingrese texto a cifrar: ")

    print("\n DES ")
    key_des = input("Ingrese key DES: ")
    iv_des = input("Ingrese IV DES: ")

    print("\n AES-256 ")
    key_aes = input("Ingrese key AES-256: ")
    iv_aes = input("Ingrese IV AES-256: ")

    print("\n 3DES ")
    key_3des = input("Ingrese key 3DES: ")
    iv_3des = input("Ingrese IV 3DES: ")

    proceso_des(texto, key_des, iv_des)
    proceso_aes256(texto, key_aes, iv_aes)
    proceso_3des(texto, key_3des, iv_3des)


if __name__ == "__main__":
    main()