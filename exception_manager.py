# _______        /\       _____V³.³.²
#/              /  \     /     \
#|  ____       /    \    |     |
#|      \     /______\   |_____/
#|      |    /        \  |     \
#\______/   /          \ \_____/
HELP_REQUEST = False
import warnings
warnings.filterwarnings("ignore")
import traceback
import json
import GABLIB.GABLIb as gL
import GABLIB.help as hp
import tkinter as tk
import sys
class ManageableException():
    def __init__(self, e: Exception = None, manageable: bool = None, ide: int = None,
                 description: str = None, traceback_str: str = None, path: str = None):
        if not isinstance(e,Exception):
             raise ValueError("invalide execption")
        self.path = path
        self.id = ide
        self.exception = e
        self.manageable = manageable
        self.description = description
        if e.__traceback__:
            self.traceback_str = self.traceback_str = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        else:
            self.traceback_str = traceback_str

    # ==== Représentation ====
    def __str__(self):
        return f"[{self.id}] {self.description} (manageable={self.manageable}) -> {self.exception}"

    def __repr__(self):
        return (f"ManageableException(id={self.id!r}, manageable={self.manageable!r}, "
                f"description={self.description!r}, exception={self.exception!r})")

    # ==== Setters / Getters ====
    def set_path(self, path: str):
        self.path = path
        return self  # chaînage

    def get_id(self): return self.id
    def get_description(self): return self.description
    def get_exception(self): return self.exception
    def get_manageable(self): return self.manageable
    def get_trash_back(self): return self.traceback_str

    # ==== Conversion ====
    def to_dict(self):
        return {
            "ide": self.id,
            "manageable": self.manageable,
            "description": self.description,
            "exception": repr(self.exception),
            "traceback": self.traceback_str
        }

    def to_json(self):
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    # ==== I/O via GABLIb ====
    def from_file(self):
        """Recharge l'instance depuis self.path via gL.jsonload()."""
        if not self.path:
            raise ValueError("Path non défini. Utilise set_path(path) avant from_file().")
        __, data = gL.jsonload(self.path)
        # Remplir l'instance
        self.id = data.get("ide", 0)
        self.manageable = data.get("manageable")
        self.description = data.get("description")
        self.exception = Exception(data.get("exception"))
        self.traceback_str = data.get("traceback")
        return self

    def save_file(self):
        """Sauvegarde l'instance (dict) via gL.jsonsave(data, path)."""
        
        if not self.path:
            raise ValueError("Path non défini. Donne un chemin à save_file(path) ou appelle set_path() avant.")
        gL.jsonsave(self.to_dict(), self.path)
        return self
    def type(self):
        return "type=ManageableException"
class terminal():
    def start(self):
        print(f"exception:{str(self.exception)}")
        print("-------------------------")
        print(f"traceback:{self.traceback_str}")
        print(f"id:{self.id}")
        print("-------------------------")
        print(f"description:{self.description}")
        
        if HELP_REQUEST:        
            ch1 = input("do you want to open the help terminal y/n (default n)")
        
            if ch1 == "y":
                root = tk.Tk()
                app = hp.HELP_terminal_GUI(root)
                root.mainloop()
            else:
                print("bye")
    def __init__(self,exception:ManageableException):
        if not isinstance(exception, ManageableException):
            raise ValueError(f"{exception} is not a ManageableException but is type: {type(exception)}")
        data = exception.to_dict()
        self.id = data.get("ide")
        self.manageable = data.get("manageable")
        self.description = data.get("description")
        self.exception = Exception(data.get("exception"))
        self.traceback_str = data.get("traceback")
        self.start()
