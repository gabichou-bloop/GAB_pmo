# _______        /\       _____V³.³.²
#/              /  \     /     \
#|  ____       /    \    |     |
#|      \     /______\   |_____/
#|      |    /        \  |     \
#\______/   /          \ \_____/
import sys,traceback,ctypes,os,platform
def _exit(Debug: bool = False, code: int = 101122):
    if Debug:
        print("ACTIVATING STOPPING SYSTEM...")
        print("DETECTING PID... [1/3]")
    pid = os.getpid()
    if Debug:
        print(f"DONE PID : {pid}")
        print("HANDLING PID... [2/3]")

    if platform.system() == "Windows":
        handle = ctypes.windll.kernel32.OpenProcess(1, False, pid)
        if Debug:
            print(f"HANDLING DONE, RESULT : {str(handle)} [2/3]")
        print(f"STOPPING, CODE : {code}...")
        ctypes.windll.kernel32.TerminateProcess(handle, code)
    else:
        print(f"STOPPING via os.kill, CODE : {code}...")
        os.kill(pid, code)

"""
GABLIB – init du package
branche GABLIb/help/exception_manager/security_center + init léger
"""
MANDATORY = [
    ("GABLIb", "gl"),  # <- tel que le fichier est écrit
    ("help", "hp"),
    ("exception_manager", "em"),
    ("security_center", "sc"),
]
import importlib
from . import simple_tkinter
for mod_name, alias in MANDATORY:
    try:
        globals()[alias] = importlib.import_module(f".{mod_name}", __package__)
    except Exception as e:
        print(f"[GABLIB] Critical module missing: {mod_name} ({e})")
        _exit(False, 400404)
# modules optionnels
try:
    from . import encoder as enc
except Exception as e:
    print(f"warning a modull is not avaible : {e}")
    enc = None
try:
    from . import decode as dec
except Exception as e:
    print(f"warning a modull is not avaible : {e}")
    dec = None
try:
    from . import terminal_maker as ter
except Exception as e:
    print(f"warning a modull is not avaible : {e}")
    ter = None
__version__ = "3.3.2"
__author__  = "Gabriel"

import os, sys, warnings, importlib
  # évite le spam du core

# ===== config partagée minimale =====
CONFIG = {
    "debug": True,
    "data_dir": os.path.join(os.path.expanduser("~"), ".gablib_data"),
}

def _safe_enable_faulthandler():
    """Active faulthandler sans planter (IDLE/fileno)."""
    try:
        import faulthandler
        if hasattr(sys.stderr, "fileno"):
            try:
                faulthandler.enable(all_threads=True)
            except Exception:
                faulthandler.enable()
    except Exception:
        pass

# ======= TA FONCTION =======
def init(debug: bool = True,
         data_dir: str | None = None,
         enable_faulthandler: bool | None = None):
    """
    Initialise GABLIB.
    - debug: active logs légers
    - data_dir: dossier pour données (par défaut ~/.gablib_data)
    - enable_faulthandler: True/False/None (None → suit debug)
    """
    CONFIG["debug"] = bool(debug)
    if data_dir:
        CONFIG["data_dir"] = str(data_dir)

    try:
        os.makedirs(CONFIG["data_dir"], exist_ok=True)
    except Exception:
        pass

    if enable_faulthandler is True or (enable_faulthandler is None and CONFIG["debug"]):
        _safe_enable_faulthandler()

    if CONFIG["debug"]:
        print(f"[GABLIB] init ok → {CONFIG['data_dir']}")

# ===== raccourcis utiles =====
# exceptions
ManageableException = em.ManageableException
ExceptionTerminal  = em.terminal
GABLIbException    = gl.GABLIbException

# outils core
jsonsave    = gl.jsonsave
jsonload    = gl.jsonload
hashtext    = gl.hashtext
popup_error = gl.popup_error
shutdown_pc = gl.shutdown_pc
handlecode  = gl.handlecode
_exit       = gl._exit
kill        = gl.kill
request_mdp = sc.request_mdp
creat_terminal = ter.creat__terminal
def open_help():
    """Lance la GUI d’aide sur le module courant."""
    import tkinter as tk
    root = tk.Tk()
    app = hp.HELP_terminal_GUI(root)
    root.mainloop()

def safe_execute(fn, *args, **kwargs):
    """Execute fn et route l’erreur en ManageableException si ça pète."""
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        mex = em.ManageableException(e, True, 0, "safe_execute captured exception")
        em.terminal(mex)

def reload():
    """Hot reload des sous-mods GABLIB (pratique en dev)."""
    importlib.reload(gl)
    importlib.reload(hp)
    importlib.reload(em)
    if enc: importlib.reload(enc)
    if dec: importlib.reload(dec)
    if CONFIG["debug"]:
        print("[GABLIB] modules reloaded.")
    return True
