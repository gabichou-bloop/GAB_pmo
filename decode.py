import GABLIB as gl
import subprocess
class DecodeException(Exception):
    pass

def execute(data, vars):
    var = data.split("=")
    if len(var) == 2:
        vars[var[0]] = var[1]
        return vars
    if len(var) > 2:
        raise DecodeException(f"unreadable var: {data}")

    parts = data.split("_")
    commande = parts[0]

    if commande == "in":
        vars[parts[1]] = input(parts[2])
    

    elif commande == "ru":
        # exécution de fichier/programme
        subprocess.run([parts[1]], check=True)

    elif commande == "sh":
        # exécution de commande shell
        cmd = " ".join(parts[1:])
        subprocess.run(cmd, shell=True, check=True)
    elif commande == "pr":
        if parts[1] in vars:
            print(vars[parts[1]])
        else:
            print(parts[1])
    elif commande == "ex":
        gl._exit()
    elif commande == "op":
        if len(parts) == 4:
            chemin, mode, variable = parts[1], parts[2], parts[3]
            if mode == "r":
                with open(chemin, "r", encoding="utf-8") as file:
                    contenu = "".join([x.strip() + "\n" for x in file.readlines()])
                vars[variable] = contenu.strip()
            elif mode == "w":
                with open(chemin, "w", encoding="utf-8") as file:
                    file.write(vars.get(variable, ""))
            else:
                raise DecodeException(f"mode open invalide: {mode}")
    elif commande != "":
        raise DecodeException(f"invalid commande: {data}")

    return vars

def execute_list(l):
    vars = {}
    for c in l:
        cc = c.strip()
        if cc:  # 🚫 ignore lignes vides
            vars = execute(cc, vars)
    return vars

def execute_file(file):
    with open(file, "r+", encoding="utf-8") as f:
        lines = f.readlines()
    return execute_list(lines)
