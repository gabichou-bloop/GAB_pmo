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
class DecodeException(Exception):
    pass
def execute(data,vars):
    
    var = data.split("=")
    if len(var) == 2:
        vars[f"{var[0]}"] = var[1]
        return vars
    if len(var) > 2:
        raise DecodeExceotion("unredable var:{data}")
    parts = data.split("_")
    commande = parts[0]
    
    if commande == "in":
        vars[f"{parts[1]}"] = input(parts[2])
    elif commande == "pr":
        if f"{parts[1]}" in vars:
            print(vars[f"{parts[1]}"])
        else:
            print([parts[1]])
    elif commande == "ex":
        pass
    else:
        raise DecodeException(f"invalid commande:{data}")
    return vars
def execute_list(l):
    vars = {}
    for c in l:
        cc = c.strip()
        vars = execute(cc,vars)
def execute_file(file):
    with open(file,"r+") as f:
        lines = f.readlines()
        execute_list(lines)
