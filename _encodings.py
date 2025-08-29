class compress_error(Exception):
    pass
def compress(texte):
    resultat = ""
    compteur = 1
    if "_" in list(texte):
        raise compress_error("invalide caracter : _")
    for i in range(1, len(texte)):
        if texte[i] == texte[i-1]:
            compteur += 1
        else:
            resultat += str(compteur) + texte[i-1] +"_" 
            compteur = 1
    # Ajouter le dernier caractère
    resultat += str(compteur) + texte[-1]
    return resultat

def compress_file(path):
    with open(path,"r+") as f:
        lines = f.readlines()
    o = path.split(".")
    outpout = o[0]+".gabi"
    with open(outpout,"w+") as f:
        for i in lines:
            cl = compress(i.strip())
            f.write(f"{cl}\n")
