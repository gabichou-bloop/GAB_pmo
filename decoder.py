class decompress_error(Exception):
    pass
def decompress(text):
    textlist = text.split("_")
    resultat = ""
    for txt in textlist:
        txtl = list(txt)
        try:
            iteration = int(txt[:-1]) 
            for i in range(0,int(iteration)):
                resultat += txt[-1] 
        except:
            raise decompress_error(f"invalid copressed data : {txt}")
    return resultat
def decompress_file(path,outpout):
    with open(path,"r+") as f:
        lines = f.readlines()
    with open(outpout,"w+") as f:
        for i in lines:
            dl = decompress(i.strip()) 
            f.write(f"{dl}\n")#
