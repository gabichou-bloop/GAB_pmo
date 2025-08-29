import GABLIB as gl
import ctypes
import json
import sys
import tkinter as tk
import warnings
from tkinter import messagebox
import os
import shutil
import hashlib
import time
import traceback
import builtins
import subprocess
class EncodeExcption(Exception):
    pass
def encode(data):
    var = data.split("=")
    if len(var) == 2:
        return(data)
    elif len(var) > 2:
        raise EncodeExcption(f"invalide definition:{data}")
    part = data.split(" ")
    commande = part[0]
    args = []
    for a in part:
        if not a == commande:
            args.append(a)
    if commande == "print":
        if len(args) == 1:
            return f"pr_{args[0]}"
        else:
            raise EncodeExcption("invalids args")
    if commande == "exit":
        if len(args) == 0:
            return f"ex"
        else:
            raise EncodeExcption("invalids args")
    if commande == "input":
        if len(args) == 2:
            return f"in_{args[0]}_{args[1]}"
        else:
            raise EncodeExcption("invalids args")
    else:
        raise EncodeExcption(f"invalids command:{data}")

def encode_list(data:list):
    resulte = []
    for a in data:
        r = encode(a)
        resulte.append(r)
    return resulte
def encode_file(file,outpout = None):
    co = 0
    with open(file,"r+") as f:
        l = f.readlines()
        for e in l:
            cl = e.strip()
            l[co] = cl
            co =+ 1

    el = encode_list(l)
    if not outpout == None:
        with open(outpout,"w+") as f:
            for e in el:
                f.write(f"{e}\n")
    else:
        o = file.split(".")
        with open(f"{o[0]}.gl","w+") as f:
            for e in el:
                f.write(f"{e}\n")
