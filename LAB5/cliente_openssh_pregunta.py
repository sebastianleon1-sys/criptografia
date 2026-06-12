import socket
import paramiko

HOST = "127.0.0.1"
PORT = 2222
USER = "prueba"
PASSWORD = "prueba"

sock = socket.create_connection((HOST, PORT))

transport = paramiko.Transport(sock)

# Banner modificado para replicar la versión del enunciado
transport.local_version = "SSH-2.0-OpenSSH_?"

transport.connect(username=USER, password=PASSWORD)

chan = transport.open_session()
chan.exec_command("echo conexion_realizada")
print(chan.recv(1024).decode(errors="ignore"))

chan.close()
transport.close()
