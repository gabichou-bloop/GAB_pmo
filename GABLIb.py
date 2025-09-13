
# _______        /\       _____V³.³.²
#/              /  \     /     \
#|  ____       /    \    |     |
#|      \     /______\   |_____/
#|      |    /        \  |     \
#\______/   /          \ \_____/
import ctypes,platform
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
from . import encoder as enc
from . import decode as dec
import builtins
import subprocess
import GABLIB.help as hp
import GABLIB.exception_manager as em
import GABLIB as gl
import signal
EXCEPTION_NUMBER = 0
MAX_EXCEPTION = 20
_ORIG = hp._ORIG
import subprocess
def unprotect_tout():
    """Restaure les fonctions originales. Renvoie True si tout est OK, False si partiel."""
    ok = True

    # os / subprocess : on peut aussi réparer via reload si besoin
    try:
        sys.exit = _ORIG.get("sys.exit", sys.exit)
    except Exception:
        ok = False
    try:
        if _ORIG.get("builtins.exit") is not None:
            builtins.exit = _ORIG["builtins.exit"]
    except Exception:
        ok = False
    try:
        if _ORIG.get("builtins.quit") is not None:
            builtins.quit = _ORIG["builtins.quit"]
    except Exception:
        ok = False
    print(f"restoration ok:{ok}")

class kill():
    def __init__(self, code=101122):
        """auto destruction multi-OS"""
        mdp_ok = gl.sc.request_mdp(input("passwort:"))
        if not mdp_ok:
            self.start(code)

    def start(self, code):
        print("STOPING...")
        print("--------------------------")
        print(f"WITH CODE: {code}")
        print("--------------------------")
        
        # [1/4] Désactivation des protections
        print("deactivatings restriction[1/4]")
        unprotect_tout()
        print("deactivation terminate[1/4]")
        
        # [2/4] Tentative de kill des autres Python
        print("starting killing [2/4]")
        print("killing...")
        self.kill_all_python()
        
        # [3/4] Terminal d'exception
        print("trying open the exception terminal[3/4]")
        try:
            raise gl.GABLIbException("""killing...
ram over loading detected
                              """)
        except Exception as e:
            et = traceback.format_exc()
            print(et)
            mex = em.ManageableException(
                Exception(e),
                True,
                1,
                "Forced termination",
                et,
                None
            )
            ter = em.terminal(mex)
        
        # Bloc final multi-OS
        print("TERMINAL FAILED[3/4]")
        print("EMERGENCY STARTED[4/4]")   
        print("SECURITY ACTIVATED")
        print("ACTIVATING ALERT STOPING SYSTEM...")
        print("***NAISTY USING DETECTED***")
        print("DETECTION THE PID... [1/3]")
        pid = os.getpid()  # PID courant
        print(f"DONE PID : {pid}")
        print("HANDLELING PID... [2/3]")

        if platform.system() == "Windows":
            handle = ctypes.windll.kernel32.OpenProcess(1, False, pid)  # PROCESS_TERMINATE = 1
            print(f"HADLING DONE, RESULT : {str(handle)}[2/3]")
            print(f"STOPING CODE : {code}...[3/3]")
            print("ERMEGENCY STOPPING[4/4]")
            ctypes.windll.kernel32.TerminateProcess(handle, code)
        else:
            print("HADLING DONE (Unix/Mac style)[2/3]")
            print(f"STOPING CODE : {code}...[3/3]")
            print("ERMEGENCY STOPPING[4/4]")
            os.kill(pid, signal.SIGKILL)

    def kill_all_python(self):
        """Tue tous les processus Python selon l'OS"""
        osname = platform.system()
        if osname == "Windows":
            targets = {"python.exe", "pythonw.exe", "py.exe"}
            for p in targets:
                try:
                    cmd = f'taskkill /IM "{p}" /F /T'
                    ret = os.system(cmd)
                    print(f"killed {p} ret={ret}")
                except Exception as e:
                    print(f"error in killing {p}: {e}")
        elif osname in ("Linux", "Darwin"):
            try:
                subprocess.run("pkill -9 python3", shell=True)
                subprocess.run("pkill -9 python", shell=True)
                print("All Python processes killed (Unix/Mac).")
            except Exception as e:
                print(f"error in killing python procs: {e}")
    print("hello from GABLIB")
class Licens:
    def __init__(self):
        """type of class"""
        # évite de print dans __init__ si possible
        self.name = "Licens"

    def show(self):
        print("this is licens")


class GABLIblicens(Licens):
    """
    licens 
    """
    def __init__(self, owner="Gabriel Teston", company="GABI INC.", version="V3.3.2"):
        super().__init__()
        self.owner = owner
        self.company = company
        self.version = version

    def show(self):
        """
        to show the licens
        """
        super().show()
        print("LICENS")
        print("----------------------------------------------------")
        print(f"no publish copyright {self.company}")
        print("----------------------------------------------------")
        print(f"contacts: {self.owner}")
        print(f"version: {self.version}")
class LicenseWarning(Warning):
    """
    WARNING → licens cert a do not publish
    """
    def __init__(self, message, dwarn=False):
        super().__init__(message)
        if dwarn:
            warnings.warn(
                "This is a license warning: copyright or license expiration alert",
                stacklevel=2
            )


class GABLIbException(Exception):
    """Exception personnalisée GABLIB."""
    def __init__(self, e):
        global EXCEPTION_NUMBER
        full_message = (
            "we are sorry an exception during the script has occurred\n"
            "----------------------------------------------------\n"
            f"{e}\n"
            "----------------------------------------------------\n"
            "contacts: Gabriel Teston"
        )
        EXCEPTION_NUMBER += 1
        ef = Exception(e)
        super().__init__(full_message)
        exc = em.ManageableException(ef,False,EXCEPTION_NUMBER,None,traceback.format_exc())
        ter = em.terminal(exc)
# Exemple d’utilisation
warnings.warn("DO NOT PUBLISH", LicenseWarning)
def _exit(Debug:bool=False,code:int = 101122):
    if Debug:
        print("ACTIVATING STOPING SYSTEM...")
        print("DETECTION THE PID... [1/3]")
    pid = os.getpid()  # PID courant
    if Debug:
        print(f"DONE PID : {pid}")
        print("HANDLELING PID... [2/3]")
    handle = ctypes.windll.kernel32.OpenProcess(1, False, pid)  # PROCESS_TERMINATE = 1
    if Debug:
        print(f"HADLING DONE, RESULT : {str(handle)}[2/3]")
    print(f"STOPING, CODE : {code}...")
    ctypes.windll.kernel32.TerminateProcess(handle, code) 

def destroy(exception="An exception occurred during the script", popup: bool = False, title="ERROR"):
    """Affiche un message (console ou popup) puis lève l'exception GABLIbException."""
    global EXCEPTION_NUMBER
    if EXCEPTION_NUMBER >= MAX_EXCEPTION:
        print("GABICHOU PROTECTION DETECTED A CPU CRASH SYSTEM")
        print("THE SCRIPT WHIL BE STOPP IN 10s")
        time.sleep(10)
        print("LAUNCHING KILLING PROTOCOL ")
        k = kill(666666)
        k.destroy()
        while True:
            time.sleep(1)
    if popup:
        root = tk.Tk()
        root.withdraw()  # Cache la fenêtre principale
        messagebox.showerror(title, exception)
        root.destroy()
    EXCEPTION_NUMBER += 1
    print(f"FATAL:{exception},code:500500")
    raise GABLIbException(Exception(exception))
def deconvert_sets(obj):
    """
    Reconstruit les sets depuis des listes marquées dans le JSON.
    On marque les sets convertis avec un dictionnaire spécial {"__set__": [...]}
    """
    if isinstance(obj, dict):
        # Si c'est un set converti
        if "__set__" in obj and isinstance(obj["__set__"], list):
            return set(obj["__set__"])
        else:
            return {k: deconvert_sets(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [deconvert_sets(i) for i in obj]
    return obj

def jsonload(jsonfile,deconvert : bool = True):
    """Charge un fichier JSON et renvoie (type, données)."""
    try:
        with open(jsonfile, "r", encoding="utf-8") as f:
            data_loaded = json.load(f)
            if deconvert:
                data_loaded = deconvert_sets(data_loaded)
            return type(data_loaded), data_loaded
    except Exception as e:
        raise GABLIbException(f"json load error str({e})")
def popup_error(title, msg):
    """Affiche une popup d'erreur."""
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(title, msg)
    root.destroy()
def convert_sets(obj):
    """
    Convertit les sets Python en un format JSON-compatible avec marqueur {"__set__": [...]}
    """
    if isinstance(obj, set):
        return {"__set__": list(obj)}
    elif isinstance(obj, dict):
        return {k: convert_sets(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_sets(i) for i in obj]
    return obj
def jsonsave(data, path, methode="w", backup=True, convert=True):
    """
    Sauvegarde des données Python dans un fichier JSON.

    data    → dict, list, etc.
    path    → chemin du fichier
    methode → "w" pour écraser, "a" pour ajouter (rarement utile en JSON)
    backup  → si True, crée une copie .bak avant d'écraser
    convert → conversion
    """
    if convert:
        data = convert_sets(data)
    else:
        warnings.warn(
            "dis is dangerous and can make any exception",
            SyntaxWarning
        )
        
    try:
        dir_path = os.path.dirname(path)
        if dir_path:  # créer le dossier uniquement si un dossier est précisé
            os.makedirs(dir_path, exist_ok=True)

        # Écriture JSON
        with open(path, methode, encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        # Sauvegarde de sécurité
        if backup and os.path.exists(path):
            shutil.copy(path, path + ".bak")
    except Exception as e:
        raise GABLIbException(f"json save error str({e})")
 
def hashtext(texte):
    "Créer un objet SHA-256 et alimenter avec les données"
    hash_obj = hashlib.sha256(texte.encode("utf-8"))


    hash_hex = hash_obj.hexdigest()
    return hash_hex
def shutdown_pc(args=""):
    subprocess.run(f"shutdown {args}")
def handlecode(code):
    stop_codes = {
        101122: "SIMPLE STOPPING",
        200001: "FORCE STOP → SECURITY-EMERGENCY TRIGERRED STOP",
        300045: "SHUTDOWN IMMEDIATE",
        400404: "PROCESS NOT FOUND - STOPPING",
        500500: "FATAL ERROR - STOP ALL",
        666666: "FORCE STOP - SECURITY TRIGGERED",
        875867: "FALSE CODE"
    }

    if code in stop_codes:
        message = stop_codes[code]
        print(f"code:{code},desription : {message}")
    else:
        print(f"[INFO] Code {code} non reconnu")
def encrypt_and_run_file(file,outpout):
    enc.encode_file(file,outpout)
    dec.execute_file(outpout)


if __name__ == "__main__":
    popup_error("warning","the modul is not make to be run")
