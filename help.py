import importlib
import inspect
import textwrap
import warnings
import builtins
import logging
import sys
import os
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
import ast
import subprocess

_ORIG = {
   "sys.exit": sys.exit,
   "builtins.exit": builtins.exit,
   "builtins.quit": builtins.quit,
   "os._exit": os._exit,
   "os.system": os.system,
   "subprocess.Popen": subprocess.Popen,
   "subprocess.run": subprocess.run,
}

# ========= PROTECTIONS (soft) =========
def protect_sys_exit():
    sys.exit = lambda *a, **k: print("[ERREUR] sys.exit() bloqué")
    builtins.exit = lambda *a, **k: print("[ERREUR] exit() bloqué")
    builtins.quit = lambda *a, **k: print("[ERREUR] quit() bloqué")
    os._exit = lambda *a, **k: print("[ERREUR] os._exit() bloqué")

def protect_os_system():
    os.system = lambda *a, **k: print("[ERREUR] os.system() bloqué")
    subprocess.Popen = lambda *a, **k: print("[ERREUR] subprocess.Popen bloqué")
    subprocess.run = lambda *a, **k: print("[ERREUR] subprocess.run bloqué")

if __name__ == "__main__":
    protect_sys_exit()
    protect_os_system()

# ========= SANDBOX FICHIERS =========
class FileSandbox:
    """Autorise l'écriture UNIQUEMENT dans --allow-write, et restaure builtins.open en sortie."""
    def __init__(self, allow_write=None):
        self.allow_write = allow_write
        self._orig_open = None

    def _check_write(self, path):
        if not self.allow_write:
            raise PermissionError("[SANDBOX] Aucune écriture autorisée.")
        apath = os.path.abspath(path)
        root = os.path.abspath(self.allow_write)
        if not (apath == root or apath.startswith(root + os.sep)):
            raise PermissionError(f"[SANDBOX] {apath} hors du dossier autorisé {self.allow_write}")

    def _guarded_open(self, file, mode='r', *a, **k):
        if any(f in mode for f in ("w", "a", "+", "x")):
            self._check_write(file)
        return self._orig_open(file, mode, *a, **k)

    def __enter__(self):
        self._orig_open = builtins.open
        builtins.open = self._guarded_open
        return self

    def __exit__(self, exc_type, exc, tb):
        builtins.open = self._orig_open
        return False

# ========= ADAPTE ICI SI BESOIN =========
import GABLIB.GABLIb as gablib
warnings.filterwarnings("ignore", message="DO NOT PUBLISH")

# ========= UTILS =========
def safe_eval(token: str):
    """Essaye de parser un littéral Python, sinon renvoie la chaîne telle quelle."""
    try:
        return ast.literal_eval(token)
    except Exception:
        return token

class GuiStream:
    """Stream qui pousse tout ce qui est écrit vers la GUI + miroir vers stdout/stderr réel."""
    def __init__(self, write_cb, fallback):
        self.write_cb = write_cb
        self.fallback = fallback
    def write(self, s):
        try:
            self.write_cb(s)
        finally:
            try:
                self.fallback.write(s)
            except Exception:
                pass
    def flush(self):
        try:
            self.fallback.flush()
        except Exception:
            pass

# ========= GUI HELP TERMINAL =========
class HELP_terminal_GUI:
    def __init__(self, root):
        self.root = root
        self.module = gablib
        self.module_name = self.module.__name__
        self.variables = {}
        self.var_history = []
        self.history = []

        # === Instances ===
        self.instances = {}           # nom -> objet
        self._inst_counter = {}       # Classe -> compteur pour noms auto
        self.current_instance = None  # nom courant (str) ou None

        self._build_gui()
        self._hook_streams()

        # warnings -> GUI
        def _showwarning(msg, cat, filename, lineno, file=None, line=None):
            self._write_gui(f"[WARNING] {cat.__name__}: {msg}\n")
        warnings.showwarning = _showwarning

        self.print_out(f"[HELP] prêt sur {self.module_name}")

    # ----- GUI de base -----
    def _build_gui(self):
        self.root.title("HELP Terminal GUI")
        self.output = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=30, width=120)
        self.output.pack(padx=5, pady=5)
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.X, padx=5, pady=5)
        self.entry = tk.Entry(frame)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", lambda e: self._handle_cmd(self.entry.get().strip()))
        tk.Button(frame, text="Exécuter", command=lambda: self._handle_cmd(self.entry.get().strip())).pack(side=tk.LEFT, padx=5)

    def _hook_streams(self):
        # route TOUT print/log vers la GUI
        sys.stdout = GuiStream(self._write_gui, sys.__stdout__)
        sys.stderr = GuiStream(self._write_gui, sys.__stderr__)
        # logging basique
        h = logging.Handler()
        def emit(record):
            try:
                msg = logging.Formatter("[LOG] %(levelname)s: %(message)s").format(record)
            except Exception:
                msg = str(record)
            self._write_gui(msg + "\n")
        h.emit = emit
        logging.getLogger().addHandler(h)
        logging.getLogger().setLevel(logging.INFO)

    def _write_gui(self, s: str):
        if not s:
            return
        self.output.insert(tk.END, s)
        self.output.see(tk.END)
        self.output.update_idletasks()

    def print_out(self, text):
        self._write_gui(text + "\n")

    def _popup_input(self, prompt):
        win = tk.Toplevel(self.root)
        win.title(prompt)
        tk.Label(win, text=prompt).pack(padx=5, pady=5)
        entry = tk.Entry(win)
        entry.pack(padx=5, pady=5)
        result = []
        def submit():
            result.append(entry.get())
            win.destroy()
        entry.bind("<Return>", lambda e: submit())
        tk.Button(win, text="OK", command=submit).pack(pady=5)
        entry.focus_set()
        self.root.wait_window(win)
        return result[0] if result else ""

    # ----- Introspection -----
    def _public_items(self):
        return [(k, v) for k, v in vars(self.module).items() if not k.startswith("_")]

    def _functions(self):
        return sorted(
            [(n, o) for n, o in self._public_items() if inspect.isfunction(o)],
            key=lambda x: x[0].lower()
        )

    def _classes(self):
        return sorted(
            [(n, o) for n, o in self._public_items() if inspect.isclass(o)],
            key=lambda x: x[0].lower()
        )

    def _resolve(self, name: str):
        # 1) module courant
        if hasattr(self.module, name):
            return getattr(self.module, name)
        # match insensible à la casse
        lname = name.lower()
        for k, v in self._public_items():
            if k.lower() == lname:
                return v
        # 2) builtins (permet execute print "yo")
        if hasattr(builtins, name):
            return getattr(builtins, name)
        # 3) notation module.attr (ex: math.sqrt)
        try:
            modname, attr = name.split(".", 1)
            m = importlib.import_module(modname)
            return getattr(m, attr)
        except Exception:
            return None

    def _sig(self, obj):
        try:
            return str(inspect.signature(obj))
        except Exception:
            return "(...)"

    def _shortdoc(self, obj, width=80):
        doc = inspect.getdoc(obj) or "Pas de documentation."
        return textwrap.shorten(doc.splitlines()[0], width=width, placeholder=" …")

    def _fulldoc(self, obj):
        return inspect.getdoc(obj) or "Pas de documentation."

    def _location(self, obj):
        try:
            path = inspect.getsourcefile(obj) or inspect.getfile(obj)
            line = inspect.getsourcelines(obj)[1]
            return f"{path}:{line}"
        except Exception:
            return "Emplacement source indisponible"

    # ----- Actions -----
    def recharger_gablib(self):
        self.print_out("[GABLIB] Rechargement…")
        importlib.reload(self.module)
        self.module_name = self.module.__name__
        self.print_out("[GABLIB] OK ✅")

    def list(self, kind="all", max_items=200):
        if kind in ("all", "func", "functions"):
            self.print_out("\n[Fonctions]")
            for n, o in self._functions()[:max_items]:
                self.print_out(f"  - {n}{self._sig(o)}  →  {self._shortdoc(o)}")
        if kind in ("all", "class", "classes"):
            self.print_out("\n[Classes]")
            for n, o in self._classes()[:max_items]:
                self.print_out(f"  - {n}  →  {self._shortdoc(o)}")

    def search(self, term: str):
        term_l = term.lower()
        found = False
        self.print_out(f"\n[Recherche] « {term} »")
        for n, o in self._functions():
            if term_l in n.lower() or term_l in (inspect.getdoc(o) or "").lower():
                self.print_out(f"  (fn) {n}{self._sig(o)}  →  {self._shortdoc(o)}")
                found = True
        for n, o in self._classes():
            if term_l in n.lower() or term_l in (inspect.getdoc(o) or "").lower():
                self.print_out(f"  (cl) {n}  →  {self._shortdoc(o)}")
                found = True
        if not found:
            self.print_out("  Aucun résultat.")

    def help_symbol(self, name: str):
        obj = self._resolve(name)
        if obj is None:
            self.print_out(f"[ERREUR] Symbole introuvable: {name}")
            return
        if inspect.isfunction(obj):
            self.print_out(f"\n=== AIDE FONCTION: {name} ===")
            self.print_out(f"Signature : {name}{self._sig(obj)}")
            self.print_out(f"Emplacement: {self._location(obj)}")
            self.print_out("\nDocstring:")
            self.print_out(self._fulldoc(obj))
        elif inspect.isclass(obj):
            self.print_out(f"\n=== AIDE CLASSE: {name} ===")
            self.print_out(f"Emplacement: {self._location(obj)}")
            self.print_out("\nDocstring:")
            self.print_out(self._fulldoc(obj))
            methods = []
            for mname, member in inspect.getmembers(obj, predicate=inspect.isfunction):
                if not mname.startswith("_") and member.__qualname__.split(".")[0] == obj.__name__:
                    methods.append((mname, member))
            if methods:
                self.print_out("\nMéthodes publiques:")
                for mname, member in sorted(methods, key=lambda x: x[0].lower()):
                    self.print_out(f"  - {mname}{self._sig(member)}  →  {self._shortdoc(member)}")
        else:
            self.print_out(f"\n=== AIDE OBJET: {name} ===")
            self.print_out(str(type(obj)))
            self.print_out(self._fulldoc(obj))

    def sig(self, name: str):
        obj = self._resolve(name)
        if obj is None:
            self.print_out(f"[ERREUR] Symbole introuvable: {name}")
            return
        self.print_out(f"{name}{self._sig(obj)}")

    # ----- Variables utilisateur -----
    def listvar(self):
        if not self.variables:
            self.print_out("[INFO] Aucune variable.")
            return
        for k, v in self.variables.items():
            self.print_out(f"{k} = {repr(v)}")

    def setvar(self, name, value):
        self.variables[name] = value
        self.var_history.append((datetime.now(), name, value))
        self.print_out(f"[OK] {name} mis à {repr(value)}")

    def getvar(self, name):
        if name in self.variables:
            self.print_out(f"{name} = {repr(self.variables[name])}")
        else:
            self.print_out(f"[ERREUR] Variable inconnue: {name}")

    def show_history(self):
        if not self.var_history:
            self.print_out("[INFO] Pas d'historique.")
            return
        for ts, name, value in self.var_history:
            self.print_out(f"{ts} : {name} = {repr(value)}")

    # ----- Changer de module -----
    def choise(self, module_name):
        try:
            self.module = importlib.import_module(module_name)
            self.module_name = self.module.__name__
            self.print_out(f"[HELP] prêt sur {self.module_name}")
        except Exception as e:
            self.print_out(f"[ERREUR] Impossible de charger module: {e}")

    # ----- Exec protégée -----
    def execute(self, fn_name, *fn_args, allow_write=None, interactive=False):
        func = self._resolve(fn_name)
        if not callable(func):
            self.print_out(f"[ERREUR] Fonction introuvable: {fn_name}")
            return

        parsed_args = []
        parsed_kwargs = {}
        for token in fn_args:
            if "=" in token and not token.strip().startswith(("'", '"')):
                k, v = token.split("=", 1)
                parsed_kwargs[k] = safe_eval(v)
            else:
                parsed_args.append(safe_eval(token))

        if interactive:
            self._interactive_loop(func, parsed_args, parsed_kwargs, allow_write)
            return

        try:
            with FileSandbox(allow_write):
                res = func(*parsed_args, **parsed_kwargs)
            if res is not None:
                self.print_out(str(res))
        except Exception as e:
            self.print_out(f"[ERREUR] lors de l'exécution: {e}")

    # ----- MODE INTERACTIF (fix complet) -----
    def _interactive_loop(self, func, args, kwargs, allow_write):
        self.print_out("[INTERACTIF] Tape 'exit' pour quitter.")
        self.print_out("Commands: set <nom> <val> | get <nom> | listvar | (vide=réexécute) |")
        self.print_out("         <args...> ex:  42  'abc'  debug=True  size=3")

        # exécution initiale
        try:
            with FileSandbox(allow_write):
                res = func(*args, **kwargs)
            if res is not None:
                self.print_out(f"[RESULT] {res}")
        except Exception as e:
            self.print_out(f"[ERREUR] {e}")

        while True:
            cmd = self._popup_input("INTERACTIF> ").strip()
            if cmd == "":
                # répéter le dernier appel
                try:
                    with FileSandbox(allow_write):
                        res = func(*args, **kwargs)
                    if res is not None:
                        self.print_out(f"[RESULT] {res}")
                except Exception as e:
                    self.print_out(f"[ERREUR] {e}")
                continue

            if cmd.lower() == "exit":
                self.print_out("[INTERACTIF] sortie.")
                break

            if cmd.startswith("set "):
                parts = cmd.split(" ", 2)
                if len(parts) == 3:
                    try:
                        val = ast.literal_eval(parts[2])
                    except Exception:
                        val = parts[2]
                    self.setvar(parts[1], val)
                else:
                    self.print_out("[ERREUR] Syntaxe: set <nom> <val>")
                continue

            if cmd.startswith("get "):
                _, name = cmd.split(" ", 1)
                self.getvar(name)
                continue

            if cmd == "listvar":
                self.listvar()
                continue

            # traiter la ligne comme de nouveaux args/kwargs
            tokens = cmd.split()
            call_args, call_kwargs = [], {}
            for t in tokens:
                if "=" in t and not t.strip().startswith(("'", '"')):
                    k, v = t.split("=", 1)
                    try:
                        v = ast.literal_eval(v)
                    except Exception:
                        pass
                    call_kwargs[k] = v
                else:
                    try:
                        call_args.append(ast.literal_eval(t))
                    except Exception:
                        call_args.append(t)

            # mémoriser
            args, kwargs = call_args, call_kwargs

            try:
                with FileSandbox(allow_write):
                    res = func(*args, **kwargs)
                if res is not None:
                    self.print_out(f"[RESULT] {res}")
            except Exception as e:
                self.print_out(f"[ERREUR] {e}")

    # ----- WHILE non bloquant (args constants) -----
    def while_exec(self, fn_name, fn_args=(), allow_write=None, interactive=False, times=None):
        """Boucle non bloquante via after()."""
        count = {"n": 0}
        def step():
            if times is not None and count["n"] >= times:
                return
            count["n"] += 1
            self.execute(fn_name, *fn_args, allow_write=allow_write, interactive=interactive)
            self.root.after(10, step)
        step()

    # ----- WHILE INTERACTIF (demande args à chaque tour) -----
    def while_interactive(self, fn_name, fn_args=(), allow_write=None, times=None, delay_ms=10):
        """Boucle interactive non-bloquante : à CHAQUE tour, on demande des args/kwargs.
           Entrée vide = répète les derniers args. 'exit' = stop la boucle."""
        func = self._resolve(fn_name)
        if not callable(func):
            self.print_out(f"[ERREUR] Fonction introuvable: {fn_name}")
            return

        state = {"n": 0, "args": [], "kwargs": {}}

        # parse init fn_args
        init_args, init_kwargs = [], {}
        for token in fn_args:
            if "=" in token and not token.strip().startswith(("'", '"')):
                k, v = token.split("=", 1)
                try:
                    v = ast.literal_eval(v)
                except Exception:
                    pass
                init_kwargs[k] = v
            else:
                try:
                    init_args.append(ast.literal_eval(token))
                except Exception:
                    init_args.append(token)
        state["args"], state["kwargs"] = init_args, init_kwargs

        self.print_out("[WHILE-INTERACTIF] 'exit' pour arrêter. Entrée vide = répète derniers args.")
        self.print_out("Ex:  42  'abc'  debug=True  size=3")

        def one_iter():
            if times is not None and state["n"] >= times:
                self.print_out("[WHILE-INTERACTIF] terminé.")
                return

            cmd = self._popup_input(f"WHILE {fn_name} (#{state['n']+1})> ").strip()
            if cmd.lower() == "exit":
                self.print_out("[WHILE-INTERACTIF] stoppé par l'utilisateur.")
                return

            if cmd != "":
                tokens = cmd.split()
                call_args, call_kwargs = [], {}
                for t in tokens:
                    if "=" in t and not t.strip().startswith(("'", '"')):
                        k, v = t.split("=", 1)
                        try:
                            v = ast.literal_eval(v)
                        except Exception:
                            pass
                        call_kwargs[k] = v
                    else:
                        try:
                            call_args.append(ast.literal_eval(t))
                        except Exception:
                            call_args.append(t)
                state["args"], state["kwargs"] = call_args, call_kwargs

            try:
                with FileSandbox(allow_write):
                    res = func(*state["args"], **state["kwargs"])
                if res is not None:
                    self.print_out(f"[RESULT #{state['n']+1}] {res}")
            except Exception as e:
                self.print_out(f"[ERREUR] {e}")

            state["n"] += 1
            self.root.after(delay_ms, one_iter)

        one_iter()

    # ===============================
    # ----- Instances & méthodes -----
    # ===============================
    def _parse_args_kwargs(self, tokens):
        args, kwargs = [], {}
        for t in tokens:
            if "=" in t and not t.strip().startswith(("'", '"')):
                k, v = t.split("=", 1)
                try:
                    v = ast.literal_eval(v)
                except Exception:
                    pass
                kwargs[k] = v
            else:
                try:
                    args.append(ast.literal_eval(t))
                except Exception:
                    args.append(t)
        return args, kwargs

    def _auto_name_for_class(self, clsname):
        n = self._inst_counter.get(clsname, 0) + 1
        self._inst_counter[clsname] = n
        return f"{clsname.lower()}_{n}"

    def new_instance(self, class_name, tokens, explicit_name=None):
        obj = self._resolve(class_name)
        if obj is None or not inspect.isclass(obj):
            self.print_out(f"[ERREUR] Classe introuvable: {class_name}")
            return
        args, kwargs = self._parse_args_kwargs(tokens)
        try:
            inst = obj(*args, **kwargs)
        except Exception as e:
            self.print_out(f"[ERREUR] Échec d'instanciation: {e}")
            return
        name = explicit_name or self._auto_name_for_class(obj.__name__)
        if name in self.instances:
            self.print_out(f"[ERREUR] Nom déjà utilisé: {name}")
            return
        self.instances[name] = inst
        self.current_instance = name
        self.print_out(f"[OK] Instance créée: {name} ← {obj.__name__}")
        return name

    def list_instances(self):
        if not self.instances:
            self.print_out("[INFO] Aucune instance.")
            return
        self.print_out("\n[Instances]")
        for n, o in self.instances.items():
            mark = "  (courante)" if self.current_instance == n else ""
            self.print_out(f"  - {n} : {type(o).__name__}{mark}")

    def use_instance(self, name):
        if name not in self.instances:
            self.print_out(f"[ERREUR] Instance inconnue: {name}")
            return
        self.current_instance = name
        self.print_out(f"[OK] Instance courante: {name}")

    def delete_instance(self, name):
        if name not in self.instances:
            self.print_out(f"[ERREUR] Instance inconnue: {name}")
            return
        del self.instances[name]
        if self.current_instance == name:
            self.current_instance = None
        self.print_out(f"[OK] Instance supprimée: {name}")

    def _call_on(self, inst_name, method_name, tokens, allow_write=None):
        if inst_name not in self.instances:
            self.print_out(f"[ERREUR] Instance inconnue: {inst_name}")
            return
        inst = self.instances[inst_name]
        if not hasattr(inst, method_name):
            self.print_out(f"[ERREUR] Méthode inconnue: {method_name} sur {inst_name}")
            return
        meth = getattr(inst, method_name)
        if not callable(meth):
            self.print_out(f"[ERREUR] {method_name} n'est pas appelable sur {inst_name}")
            return

        args, kwargs = self._parse_args_kwargs(tokens)
        try:
            with FileSandbox(allow_write):
                res = meth(*args, **kwargs)
            if res is not None:
                self.print_out(str(res))
        except Exception as e:
            self.print_out(f"[ERREUR] lors de l'appel: {e}")

    def call_current(self, method_name, tokens, allow_write=None):
        if not self.current_instance:
            self.print_out("[ERREUR] Aucune instance courante. Utilise 'use <nom>' ou 'callon <nom>.<methode>'.")
            return
        self._call_on(self.current_instance, method_name, tokens, allow_write=allow_write)

    # ----- Parsing des commandes -----
    def _handle_cmd(self, cmd):
        if not cmd:
            return
        self.history.append(cmd)
        self.entry.delete(0, tk.END)

        parts = cmd.split()
        head = parts[0].lower()
        args = parts[1:]

        if head == "help" and not args:
            self.afficher_aide()
        elif head == "list":
            kind = "all"
            if args:
                if args[0] in ("functions", "func"):
                    kind = "functions"
                elif args[0] in ("classes", "class"):
                    kind = "classes"
            self.list(kind)
        elif head == "search" and args:
            self.search(" ".join(args))
        elif head == "help" and args:
            self.help_symbol(" ".join(args))
        elif head == "sig" and args:
            self.sig(" ".join(args))
        elif head == "gablib":
            self.recharger_gablib()
        elif head == "choise" and args:
            self.choise(args[0])
        elif head == "execute" and args:
            allow_write = None
            interactive = False
            parsed = []
            i = 0
            while i < len(args):
                a = args[i]
                if a == "--interactive":
                    interactive = True
                elif a == "--allow-write" and i + 1 < len(args):
                    allow_write = args[i + 1]
                    i += 1
                else:
                    parsed.append(a)
                i += 1
            if not parsed:
                self.print_out("[ERREUR] Pas de fonction à exécuter.")
                return
            fn_name, *fn_args = parsed
            self.execute(fn_name, *fn_args, allow_write=allow_write, interactive=interactive)
        elif head == "while" and args:
            allow_write = None
            interactive = False
            times = None
            delay_ms = 10
            parsed = []
            i = 0
            while i < len(args):
                a = args[i]
                if a == "--interactive":
                    interactive = True
                elif a == "--allow-write" and i + 1 < len(args):
                    allow_write = args[i + 1]
                    i += 1
                elif a == "--times" and i + 1 < len(args):
                    try:
                        times = int(args[i + 1])
                    except:
                        times = None
                    i += 1
                elif a == "--delay" and i + 1 < len(args):
                    try:
                        delay_ms = int(args[i + 1])
                    except:
                        delay_ms = 10
                    i += 1
                else:
                    parsed.append(a)
                i += 1

            if not parsed:
                self.print_out("[ERREUR] Pas de fonction à exécuter.")
                return

            fn_name, *fn_args = parsed
            if interactive:
                self.while_interactive(fn_name, tuple(fn_args), allow_write=allow_write, times=times, delay_ms=delay_ms)
            else:
                self.while_exec(fn_name, tuple(fn_args), allow_write=allow_write, interactive=False, times=times)

        # === Instances commands ===
        elif head == "new" and args:
            # new <Classe> [--name NOM] [args/kwargs...]
            cls = args[0]
            tokens = []
            explicit_name = None
            i = 1
            while i < len(args):
                a = args[i]
                if a == "--name" and i + 1 < len(args):
                    explicit_name = args[i + 1]
                    i += 1
                else:
                    tokens.append(a)
                i += 1
            self.new_instance(cls, tokens, explicit_name=explicit_name)

        elif head == "instlist":
            self.list_instances()

        elif head == "use" and args:
            self.use_instance(args[0])

        elif head == "delinst" and args:
            self.delete_instance(args[0])

        elif head == "call" and args:
            # call [--allow-write CHEMIN] <methode> [args/kwargs...]
            allow_write = None
            parsed = []
            i = 0
            while i < len(args):
                a = args[i]
                if a == "--allow-write" and i + 1 < len(args):
                    allow_write = args[i + 1]
                    i += 1
                else:
                    parsed.append(a)
                i += 1
            if not parsed:
                self.print_out("[ERREUR] Pas de méthode.")
                return
            method = parsed[0]
            tokens = parsed[1:]
            self.call_current(method, tokens, allow_write=allow_write)

        elif head == "callon" and args:
            # callon [--allow-write CHEMIN] <NOM>.<methode> [args/kwargs...]
            allow_write = None
            parsed = []
            i = 0
            while i < len(args):
                a = args[i]
                if a == "--allow-write" and i + 1 < len(args):
                    allow_write = args[i + 1]
                    i += 1
                else:
                    parsed.append(a)
                i += 1
            if not parsed:
                self.print_out("[ERREUR] Pas de cible.")
                return
            target = parsed[0]
            if "." not in target:
                self.print_out("[ERREUR] Syntaxe: callon <NOM>.<methode> ...")
                return
            inst_name, method = target.split(".", 1)
            tokens = parsed[1:]
            self._call_on(inst_name, method, tokens, allow_write=allow_write)

        elif head == "listvar":
            self.listvar()
        elif head == "setvar" and len(args) >= 2:
            self.setvar(args[0], safe_eval(" ".join(args[1:])))
        elif head == "getvar" and args:
            self.getvar(args[0])
        elif head == "history":
            self.show_history()
        elif head == "exit":
            self.root.destroy()
        else:
            self.print_out(f"[ERREUR] commande inconnue: {cmd}")

    def afficher_aide(self):
        self.print_out("""
=== HELP TERMINAL ===
Commandes:
  help                             → Ce menu
  list                             → Liste fonctions et classes
  list functions|classes           → Filtre
  search <mot>                     → Recherche noms+docs
  help <nom>                       → Aide détaillée
  sig <nom>                        → Signature
  gablib                           → Recharger le module courant
  choise <MODULE>                  → Changer de module

  execute [--allow-write CHEMIN] [--interactive] <fn> [args...]
  while   [--times N] [--delay ms] [--allow-write CHEMIN] [--interactive] <fn> [args...]

  # Instances:
  new <Classe> [--name NOM] [args/kwargs...]      → créer et mémoriser une instance
  instlist                                        → lister les instances
  use <NOM>                                       → définir l’instance courante
  delinst <NOM>                                   → supprimer une instance
  call [--allow-write CHEMIN] <méthode> [...]     → appeler sur l’instance courante
  callon [--allow-write CHEMIN] <NOM>.<methode> [...] → appeler sur une instance précise

  listvar / setvar / getvar        → Variables utilisateur
  history                          → Historique setvar
  exit                             → Quitter
=====================
""")

# ========= MAIN =========
if __name__ == "__main__":
    root = tk.Tk()
    app = HELP_terminal_GUI(root)
    root.mainloop()
