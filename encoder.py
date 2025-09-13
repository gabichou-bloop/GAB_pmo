class EncodeExcption(Exception):
    pass

def encode(data):
    var = data.split("=")
    if len(var) == 2:
        return data
    elif len(var) > 2:
        raise EncodeExcption(f"invalide definition:{data}")
    
    part = data.split(" ")
    commande = part[0]
    args = [a for a in part[1:] if a]

    if commande == "print":
        if len(args) == 1:
            return f"pr_{args[0]}"
        else:
            raise EncodeExcption("invalid args for print")

    elif commande == "exit":
        if len(args) == 0:
            return "ex"
        else:
            raise EncodeExcption("invalid args for exit")

    elif commande == "input":
        if len(args) == 2:
            return f"in_{args[0]}_{args[1]}"
        else:
            raise EncodeExcption("invalid args for input")

    elif commande == "open":
        if len(args) == 3:
            return f"op_{args[0]}_{args[1]}_{args[2]}"
        else:
            raise EncodeExcption("invalid args for open")

    elif commande == "run":
        if len(args) == 1:
            return f"ru_{args[0]}"
        else:
            raise EncodeExcption("invalid args for run")

    elif commande == "runshell":
        if len(args) >= 1:
            # encode en sh_arg1_arg2...
            return "sh_" + "_".join(args)
        else:
            raise EncodeExcption("invalid args for runshell")

    elif commande != "":
        raise EncodeExcption(f"invalid command:{data}")

def encode_list(data:list):
    resulte = []
    for a in data:
        r = encode(a)
        resulte.append(r)
    return resulte

def encode_file(file, outpout=None):
    with open(file, "r+", encoding="utf-8") as f:
        l = [e.strip() for e in f.readlines() if e.strip()]

    el = encode_list(l)
    if outpout:
        with open(outpout, "w+", encoding="utf-8") as f:
            for e in el:
                f.write(f"{e}\n")
    else:
        o = file.split(".")
        with open(f"{o[0]}.gl", "w+", encoding="utf-8") as f:
            for e in el:
                f.write(f"{e}\n")
