import sys
from ziper import decoder
from ziper import _encodings   # ou codec_enc si tu as renommé
import tkinter as tk
from tkinter import messagebox        
class app(tk.Tk):
    def __init__(self,path):
        super().__init__()
        self.title("")
        self.path = path
        o = path.split(".")
        self.outpout = o[0] + ".txt"
        label = tk.Label(self, text=f"{path} <--> {self.outpout}", font=("Arial", 14))
        label.pack(pady=10)
        self.btn = tk.Button(self, text="Extract",
                            command=self.decode)
        self.btn.pack(pady=20)
        self.bt = tk.Button(self, text="Encode",
                            command=self.encode)
        self.bt.pack(pady=20)
    def run(self):
        succes = True
        
        self.mainloop()

    def decode(self):
        succes = True
        try:
            decoder.decompress_file(self.path,self.outpout)
        except Exception as e:
            messagebox.showerror("error in job",e)
            succes =False
        if succes:
            messagebox.showinfo(".gabi tool","job terminate")
            self.destroy()
    def encode(self):
        try:
            _encodings.compress_file(self.path)
            succes = True
        except Exception as e:
            messagebox.showerror("error in job",e)
            succes =False
            
        if succes:
            messagebox.showinfo(".gabi tool","job terminate")
            self.destroy()
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""usage:
--compress [path]
--decompress [path] [output]
""")
        sys.exit(1)

    action = sys.argv[1]

    if action == "--compress" and len(sys.argv) == 3:
        try:
            _encodings.compress_file(sys.argv[2])
        except Exception as e:
            print(f"the action could not completed : {e}")

    elif action == "--decompress" and len(sys.argv) == 4:
        try:
            decoder.decompress_file(sys.argv[2], sys.argv[3])
        except Exception as e:
            print(f"the action could not completed : {e}")
    

    else:
        a = app(action)
        a.run()
        
