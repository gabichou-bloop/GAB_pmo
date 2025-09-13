import base64
from collections import Counter
import statistics

class encode_hash_error(Exception):
    pass
def encode(texte, magique=5, size=256):
    if texte == "":
        raise encode_hash_error("invalide hash") 
    resultat = []
    buffer = bytearray(texte.encode("utf-8"))
    co = 0

    # Normaliser magique
    magique = magique % 256 or 1

    # 🔥 Rallonge jusqu'à atteindre la taille demandée (en octets, pas en chars)
    while len(buffer) < size:
        try:
            val = (magique ** (buffer[co] * 7)) % 256
        except IndexError:
            val = (magique ** magique) % 256
        buffer.append(val)
        co += 1

    # Calcul principal sur chaque octet
    nextb = buffer[(len(buffer)-1)]
    for i, b in enumerate(buffer):
        # ajout du rang i dans le calcul pour différencier les positions
        b = ((b + magique) ** (nextb + co + magique + i)*7) % 256
        b = (b + nextb + (magique * 11) + co + i) % 256
        resultat.append(b)
        nextb = b

    # Sortie en Base64 UTF-8 safe
    return base64.b64encode(bytes(resultat)).decode("utf-8")
from math import gcd
from functools import reduce
import itertools
import string
from concurrent.futures import ThreadPoolExecutor, as_completed

def brute_worker(hash_cible, magique, size, mot):
    """Teste un mot et renvoie s'il correspond"""
    return mot if encode(mot, magique, size) == hash_cible else None

def brute_force_threads(hash_cible, magique=5, size=256, alphabet=None):
    """
    Brute force avec threads (incrémental sur toutes les longueurs possibles).
    S'arrête uniquement quand le mot de passe est trouvé.
    """
    if alphabet is None:
        alphabet = string.ascii_lowercase + string.digits + " "  # extensible
    
    longueur = 1
    while True:  # pas de max, on augmente indéfiniment
        print(f"👉 Recherche avec longueur {longueur} ...")
        combos = ("".join(c) for c in itertools.product(alphabet, repeat=longueur))

        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(brute_worker, hash_cible, magique, size, mot): mot for mot in combos}
            
            for future in as_completed(futures):
                result = future.result()
                if result:  # trouvé !
                    executor.shutdown(cancel_futures=True)
                    return result, longueur
        longueur += 1


def analyse(hash_b64, taille_originale):
    data = base64.b64decode(hash_b64.encode("utf-8"))

    vrai_hash = data[:taille_originale]
    signature = data[taille_originale:]

    return (
        base64.b64encode(vrai_hash).decode("utf-8"),
        base64.b64encode(signature).decode("utf-8")
    )
import math
def detect_magique_avance(hash_bytes, max_cycle=128):
    """Détection du magique via analyse des sous-cycles répétitifs."""
    from collections import Counter
    import base64

    best_cycle = None
    best_score = 0
    best_seq = None

    n = len(hash_bytes)
    for taille in range(2, max_cycle):
        motif = hash_bytes[:taille]
        repete = sum(
            1 for i in range(n) if hash_bytes[i] == motif[i % taille]
        )
        score = repete / n
        if score > best_score:
            best_score = score
            best_cycle = taille
            best_seq = motif

    dist = Counter(hash_bytes)
    magique_estime = max(best_seq, key=best_seq.count) if best_seq else dist.most_common(1)[0][0]

    return {
        "magique_estimé": magique_estime,
        "cycle_detecté": best_cycle,
        "score": best_score,
        "sequence_cycle": list(best_seq) if best_seq else None,
        "distribution": dist.most_common(10),
        "signature": base64.b64encode(hash_bytes).decode("utf-8")
    }
# Exemple d'utilisation

import random
def hex(txt):
    return txt.encode("utf-8").hex()
def encoded(txt):
    return hex(encode(txt))
# Exemple d'utilisation
if __name__ == "__main__":
    hash_cible = "eXl5RVUVZSUl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5Q=="

    mot, taille = brute_force_threads(hash_cible, magique=5, size=256)

    if mot:
        print(f"✅ Trouvé ! Mot de passe = '{mot}' (longueur {taille})")
    else:
        print("❌ Pas trouvé dans la limite donnée")
