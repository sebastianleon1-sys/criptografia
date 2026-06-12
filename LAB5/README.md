# Laboratorio 5 - Criptografía y Seguridad en Redes

Este laboratorio trabaja con Docker, OpenSSH y análisis de tráfico SSH. El objetivo es levantar distintos clientes SSH en contenedores Ubuntu, capturar el tráfico generado durante el handshake, obtener el HASSH de cada cliente y modificar el patrón de negociación del servidor.

## Contenido del laboratorio

El proyecto incluye:

* Contenedores Docker para:

  * C1: Ubuntu 16.10
  * C2: Ubuntu 18.10
  * C3: Ubuntu 20.10
  * C4/S1: Ubuntu 22.10
* Servidor SSH S1 implementado en el contenedor C4/S1.
* Usuario de prueba para conexión SSH.
* Capturas de tráfico SSH.
* Obtención de HASSH para cada cliente.
* Replicación del banner `SSH-2.0-OpenSSH_?`.
* Modificación de configuración SSH para reducir el `Server Key Exchange Init` a menos de 300 bytes.
* Informe en LaTeX.

## Requisitos

Para ejecutar el laboratorio se requiere:

* Linux Fedora o distribución compatible.
* Docker.
* Docker Compose.
* tcpdump.
* tshark / Wireshark CLI.
* Python 3.
* Paramiko, para la replicación del banner SSH.

Instalación de dependencias en Fedora:

```bash
sudo dnf update -y
sudo dnf install -y docker docker-compose wireshark-cli tcpdump python3-paramiko
```

Activar Docker:

```bash
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

Luego cerrar sesión y volver a entrar, o ejecutar:

```bash
newgrp docker
```

## Levantar los contenedores

Desde la carpeta del laboratorio:

```bash
docker compose up -d --build
```

Verificar que los contenedores estén activos:

```bash
docker ps
```

Deben aparecer los contenedores:

```text
C1
C2
C3
C4S1
```

## Usuario SSH de prueba

El servidor S1 se ejecuta en el contenedor C4/S1.

Credenciales utilizadas:

```text
Usuario: prueba
Contraseña: prueba
```

La IP del servidor S1 dentro de la red Docker es:

```text
172.30.0.22
```

## Prueba de conexión SSH

Ejemplo desde C1 hacia S1:

```bash
docker exec -it C1 ssh -o StrictHostKeyChecking=no prueba@172.30.0.22
```

Contraseña:

```text
prueba
```

Para salir de la sesión SSH:

```bash
exit
```

## Captura de tráfico SSH

Ejemplo de captura para C1:

Terminal 1:

```bash
docker exec -it C1 bash
tcpdump -i eth0 -w /tmp/c1_s1.pcap host 172.30.0.22 and port 22
```

Terminal 2:

```bash
docker exec -it C1 ssh -o StrictHostKeyChecking=no prueba@172.30.0.22
```

Luego salir de la conexión SSH y detener tcpdump con `Ctrl + C`.

Copiar la captura al host:

```bash
docker cp C1:/tmp/c1_s1.pcap ./pcaps/c1_s1.pcap
```

Analizar el tráfico:

```bash
tshark -r ./pcaps/c1_s1.pcap -Y "tcp.port == 22" -T fields \
-e frame.number \
-e frame.len \
-e ip.src \
-e ip.dst \
-e _ws.col.Protocol \
-e _ws.col.Info | head -n 30
```

El mismo procedimiento se repite para C2 y C3, cambiando el nombre del contenedor y el archivo `.pcap`.

## Captura de C4/S1 usando loopback

Como C4 también funciona como servidor S1, la captura se realiza sobre la interfaz `lo`.

Terminal 1:

```bash
docker exec -it C4S1 bash
tcpdump -i lo -w /tmp/c4_lo.pcap port 22
```

Terminal 2:

```bash
docker exec -it C4S1 ssh -o StrictHostKeyChecking=no prueba@127.0.0.1
```

Copiar la captura:

```bash
docker cp C4S1:/tmp/c4_lo.pcap ./pcaps/c4_lo.pcap
```

Analizar:

```bash
tshark -r ./pcaps/c4_lo.pcap -Y "tcp.port == 22" -T fields \
-e frame.number \
-e frame.len \
-e ip.src \
-e ip.dst \
-e _ws.col.Protocol \
-e _ws.col.Info | head -n 30
```

## Obtención de HASSH

Primero verificar que tshark soporte HASSH:

```bash
tshark -G fields | grep -i hassh
```

Obtener HASSH de un cliente, por ejemplo C1:

```bash
tshark -r ./pcaps/c1_s1.pcap -Y "ssh.kex.hassh" -T fields \
-e frame.number \
-e ip.src \
-e ip.dst \
-e ssh.kex.hassh \
-e ssh.kex.hassh_algorithms
```

Para C2, C3 y C4 se cambia el archivo `.pcap` correspondiente.

## Replicación del banner SSH-2.0-OpenSSH_?

Para replicar el banner del cliente se utilizó un cliente en Python con Paramiko, modificando el atributo `local_version`.

Ejecutar:

```bash
python3 cliente_openssh_pregunta.py
```

Capturar el tráfico hacia el puerto expuesto del servidor:

```bash
sudo tcpdump -i any -w ./pcaps/openssh_pregunta.pcap port 2222
```

Analizar:

```bash
tshark -r ./pcaps/openssh_pregunta.pcap -Y "tcp.port == 2222" -T fields \
-e frame.number \
-e frame.len \
-e ip.src \
-e ip.dst \
-e _ws.col.Protocol \
-e _ws.col.Info | head -n 30
```

El resultado esperado es observar:

```text
Client: Protocol (SSH-2.0-OpenSSH_?)
```

## Reducción del Server Key Exchange Init

Para reducir el `Server Key Exchange Init` a menos de 300 bytes, se utilizó una configuración mínima de `sshd` en el puerto 2223.

Archivo de configuración usado:

```text
Port 2223
ListenAddress 0.0.0.0

HostKey /etc/ssh/ssh_host_ed25519_key

PasswordAuthentication yes
PermitRootLogin yes
UsePAM no

KexAlgorithms curve25519-sha256
HostKeyAlgorithms ssh-ed25519
Ciphers aes128-ctr
MACs hmac-sha2-256
Compression no

PidFile /tmp/sshd_min.pid
```

Levantar el servidor mínimo dentro de C4/S1:

```bash
docker exec -it C4S1 bash
/usr/sbin/sshd -f /tmp/sshd_config_min -E /tmp/sshd_min.log
```

Capturar tráfico:

```bash
tcpdump -i lo -w /tmp/kei_menor_300.pcap port 2223
```

Conectarse al servidor mínimo:

```bash
docker exec -it C4S1 ssh -p 2223 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null prueba@127.0.0.1
```

Copiar captura:

```bash
docker cp C4S1:/tmp/kei_menor_300.pcap ./pcaps/kei_menor_300.pcap
```

Analizar:

```bash
tshark -r ./pcaps/kei_menor_300.pcap -Y "tcp.port == 2223" -T fields \
-e frame.number \
-e frame.len \
-e ip.src \
-e ip.dst \
-e _ws.col.Protocol \
-e _ws.col.Info | head -n 20
```

El resultado obtenido fue:

```text
Server: Key Exchange Init = 226 bytes
```

Por lo tanto, se cumple la condición solicitada de ser menor a 300 bytes.

## Informe

El informe se encuentra en formato LaTeX:

```text
lab05_informe.tex
```

También se incluye una versión compilada en PDF, si está disponible.

## Estructura sugerida del proyecto

```text
lab5/
├── C1/
│   └── Dockerfile
├── C2/
│   └── Dockerfile
├── C3/
│   └── Dockerfile
├── C4S1/
│   └── Dockerfile
├── Desarrollo/
│   └── capturas utilizadas en el informe
├── pcaps/
│   └── capturas de tráfico .pcap
├── cliente_openssh_pregunta.py
├── docker-compose.yml
├── lab05_informe.tex
├── README.md
└── Informe_Laboratorio_5.pdf
```

## Autores

* Sebastián León

## Observación

Las capturas incluidas en el informe corresponden a las evidencias relevantes del laboratorio. No se utilizaron todas las capturas generadas, ya que algunas correspondían a pruebas repetidas o salidas duplicadas.
