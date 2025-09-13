import tkinter as tk

class SimpleTk(tk.Tk):
    def __init__(self, title="Formulaire", size="420x380"):
        super().__init__()
        self.title(title); self.geometry(size)
        self.entries = {}   # name -> Entry
        self.texts = {}     # name -> Text
        self.labels = []
        self.boutons = []


    # --- champs 1 ligne ---
    def add_entry(self, name, label=None, default="", password=False, validate=None):
        """
        name: clé interne
        label: texte au-dessus (facultatif)
        default: valeur initiale
        password: True => masque avec '*'
        validate: fonction(str)->bool, pour valider à la frappe
        """
        if label:
            tk.Label(self, text=label).pack(anchor="w", padx=8, pady=(8,0))
        vcmd = None
        if validate:
            # validation à la frappe
            vcmd = (self.register(lambda s: (validate(s) or s == "")), "%P")
        e = tk.Entry(self, show="*" if password else "", validate="key" if vcmd else "none",
                     validatecommand=vcmd)
        e.insert(0, default)
        e.pack(fill="x", padx=8, pady=6)
        self.entries[name] = e
        
        return e

    def get_entry(self, name) -> str:
        return self.entries[name].get()

    def set_entry(self, name, value: str):
        e = self.entries[name]; e.delete(0, tk.END); e.insert(0, value)
    def set_ico(self, ico_file):
        self.iconbitmap(ico_file)  
    # --- zone multi-lignes ---
    def add_text(self, name, label=None, height=6, default=""):
        if label:
            tk.Label(self, text=label).pack(anchor="w", padx=8, pady=(8,0))
        t = tk.Text(self, height=height)
        if default:
            t.insert("1.0", default)
        t.pack(fill="both", expand=True, padx=8, pady=6)
        self.texts[name] = t
        return t

    def get_text(self, name) -> str:
        return self.texts[name].get("1.0", "end-1c")

    def set_text(self, name, value: str):
        t = self.texts[name]; t.delete("1.0", tk.END); t.insert("1.0", value)

    # utilitaire
    def add_button(self, texte, commande=None):
        btn = tk.Button(self, text=texte, command=commande)
        btn.pack(pady=5)
        self.boutons.append(btn)
        return btn

    def add_label(self, texte):
        lbl = tk.Label(self, text=texte, font=("Arial", 12))
        lbl.pack(pady=5)
        self.labels.append(lbl)
        return lbl
    def edit_label(self, index, nouveau_texte):
        """Modifie le texte du label à l'index donné"""
        if 0 <= index < len(self.labels):
            self.labels[index].config(text=nouveau_texte)
        else:
            print(f"[ERREUR] Aucun label à l'index {index}")