import base64

def inspect_signature(signature_b64: str):
    decoded = base64.b64decode(signature_b64)

    print("=== Décimal (liste d’octets) ===")
    print(list(decoded))
    print()

    print("=== Hexadécimal ===")
    print(decoded.hex())
    print()

    print("=== Format safe (\\x??) ===")
    print("".join(f"\\x{b:02x}" for b in decoded))
    print()

    print("=== Essais d'affichage texte ===")
    for enc in ["utf-8", "latin-1", "cp1252", "ascii"]:
        try:
            text = decoded.decode(enc, errors="replace")
            print(f"{enc.upper()} : {text}")
        except Exception as e:
            print(f"{enc.upper()} : [erreur: {e}]")

# Exemple d’utilisation
if __name__ == "__main__":
    sig = "Xa9Z4eVBYfMrff//AQH/Af///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////w=="
    inspect_signature(sig)
 