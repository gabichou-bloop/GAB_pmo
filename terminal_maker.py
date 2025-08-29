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
import GABLIB.help as hp
import GABLIB.exception_manager as em
import GABLIB as gl
import shlex
def creat__terminal(name, functions):
    for fi in functions:
        globals()[fi.__name__] = fi
    result = {}
    command_id = 0    
    while True:
        try:
            cmds = input(name)
            cmd = shlex.split(cmds)
            if cmds != "":
                nom_fonction = cmd[0]
                args = []

                for a in cmd:
                    string = False
                    if a != cmd[0]:
                        for b in list(a):
                            if b == "'":
                                string = True
                        if a == "True":
                            args.append(True)
                        elif a == "False":
                            args.append(False)
                        elif string:
                            args.append(f"{a}")
                        else:
                            args.append(a)
                if nom_fonction in globals():
                    try:
                        result[f"{nom_fonction}_{command_id}"] = (globals()[nom_fonction](*args))  # appelle dire("Gabi", 15)
                        command_id =+ 1 
                    except Exception as e:
                        print(f"error : [{e}]")
                else:
                    print(f"no fuction Fonction with name:{nom_fonction}")
                
        except KeyboardInterrupt:
            break
    return result
