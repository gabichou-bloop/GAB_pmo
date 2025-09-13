import ziper as zp
from GABLIB.vpn.keygen import generate_key as gen
import base64

class crypt_execption(Exception):
    pass

class securcrypt_key():
    def __init__(self, key, magique=255):
        try:
            self.key = zp.decoder.decompress(str(key))
        except:
            self.key = key
        self.mag = magique

    def get_key(self):
        return self.key

    def get_mag(self):
        return self.mag

    def get_sing(self):
        b = list(self.key.encode("utf-8"))
        bite = "".join(str(c) for c in b)

        val = int(bite) % (self.mag * 1000 or 1)

        modulo = int("".join(str((x * self.mag) % 997) for x in b)) + int(bite) + self.mag or 1
        sing = (val ** self.mag) % modulo

        n = 3
        sing = str(sing)
        morceaux = [sing[i:i+n] for i in range(0, len(sing), n)]

        try:
            morceaux_int = [int(m) % 256 for m in morceaux]
            return bytes(morceaux_int).decode("utf-8", errors="ignore"), morceaux_int
        except Exception as e:
            raise crypt_execption(f"decode error: {e}")
    def __str__(self):
        sing,bite=self.get_sing()
        return sing
    def __int__(self):
        _, singb = self.get_sing()
        return int("".join(str(c) for c in singb))

def gen_key():
    key = gen()
    return zp._encodings.compress(key), key

def crypt(data: str, key: securcrypt_key) -> str:
    if not isinstance(key, securcrypt_key):
        raise crypt_execption(f"invalide key: {key}")
    count = 0
    for _ in data:
        count += 1
        if "_" in data:
            datal = list(data)
            if len(datal) > 1:
                if datal[count] == "@":
                    raise crypt_execption(f"invalide data : {data}")

    # 🔹 utiliser la valeur entière (via __int__)
    signed_data = data + "_@" + str(int(key))

    # transformer en int puis bytes
    datab = int.from_bytes(signed_data.encode("utf-8"), "big")
    mixed_bytes = datab.to_bytes((datab.bit_length() + 7) // 8, "big")

    return base64.b64encode(mixed_bytes).decode("utf-8"), signed_data
def verify_signature(signed_data: str, key: securcrypt_key) -> bool:
    if "_@" not in signed_data:
        raise crypt_execption("données signées invalides (manque _@)")
    msg, sig = signed_data.split("_@", 1)

    # recalculer la signature attendue
    _, singb = key.get_sing()
    expected_bite = "".join(str(c) for c in singb)

    return sig == expected_bite

def decrypt(encoded: str, key: securcrypt_key) -> str:
    # décodage base64 -> bytes -> int -> string
    mixed_bytes = base64.b64decode(encoded)
    datab = int.from_bytes(mixed_bytes, "big")
    decoded = datab.to_bytes((datab.bit_length() + 7) // 8, "big").decode("utf-8", errors="strict")

    # ⚡ séparer message et signature
    msg, sig = decoded.split("_@", 1)

    # (optionnel) vérifier la signature
    _, singb = key.get_sing()
    expected_bite = "".join(str(c) for c in singb)
    if sig != expected_bite:
        raise crypt_execption("signature invalide !")

    return msg

if __name__ == "__main__":
    # 🔹 tests
    keyc,key =gen_key()
    a = securcrypt_key(keyc, 100)
    sig, raw = a.get_sing()
    print(f"Clé={key},Clè compresser = {keyc} , mag=100 =>", sig, "| Bytes:", raw)
    crypted,singed =crypt("abcdefg",a)
    print("crypter : ",crypted,"singed =>",singed,"decrypter =>",decrypt(crypted,a))
    print("singatur valide: ",verify_signature(singed,a))