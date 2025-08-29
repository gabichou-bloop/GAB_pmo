import secrets
import string

def generate_key(length=32):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

if __name__ == "__main__":
    key = generate_key(256)  # longueur par défaut = 32
    print("🔑 Secure Rescue Key générée :")
    print(key)
