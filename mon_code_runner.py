
import sys
import GABLIB.decoder as decoder

CODE = ['in_nom_EntreTonPrénom:', 'pr_nom', 'caca = mdr', 'op_txt.txt_w_caca']

if __name__ == "__main__":
    try:
        decoder.execute_list(CODE)
    except Exception as e:
        print("[ERREUR] :", e)
        sys.exit(1)
