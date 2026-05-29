cat > LAB4/README.md << 'EOF'

# Laboratorio 4 - Criptografía

Este laboratorio implementa un programa en Python para cifrar y descifrar mensajes utilizando cifrado simétrico con los algoritmos DES, AES-256 y 3DES en modo CBC.

El programa solicita desde la terminal:

- Texto a cifrar.
- Clave para cada algoritmo.
- Vector de inicialización IV para cada algoritmo.

Además, valida y ajusta los tamaños de clave e IV según los requisitos de cada algoritmo.

## Requisitos

- Python 3
- pip
- Entorno virtual de Python
- pycryptodome

## Crear entorno virtual

Desde la carpeta `LAB4`, ejecutar:

```bash
python3 -m venv venv
```
