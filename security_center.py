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
def lock_session():
    
    subprocess.run("TASKKILL /IM explorer.exe /F", shell=True)

def unlock_session():
    subprocess.run("start explorer.exe",shell=True)
def setup_mdp(mdp,file ="code.pem"):
    mdp = gl.gl.hashtext(mdp)
    with open(file,"w+") as f:
        f.write(mdp)
def check_mdp(mdp,file = "code.pem",exitb = False):
    try:
        with open(file,"r+") as f:
            lines = f.readlines()
            codehash = lines[0].strip()
    except:
        return False
    if codehash == gl.gl.hashtext(mdp):
        unlock_session()
        return True
    else:
        if exitb:
            gl._exit(875867)
        else:
            print("False code")
            return False
def request_mdp(mdp,file = "code.pem",exitb = False):
    lock_session()
    try:
        mdp_ok = check_mdp(mdp,file,exitb)
    except:
        print("error")
        mdp_ok = False
    return mdp_ok

