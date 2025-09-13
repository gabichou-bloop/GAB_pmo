import shlex

class TerminalException(Exception):
    pass

def create_terminal(prompt: str, functions: list):
    """
    Create a simple interactive terminal.
    
    Args:
        prompt (str): The prompt string (e.g. "GL>> ").
        functions (list): A list of Python functions to expose inside the terminal.
    
    Returns:
        dict: A dictionary mapping "function_id" to each function result.
    """
    # Register functions globally
    for fn in functions:
        globals()[fn.__name__] = fn

    results = {}
    history = []
    command_id = 0

    while True:
        try:
            raw = input(prompt).strip()
            if not raw:
                continue

            # special command: history
            if raw == "history":
                print("=== Command History ===")
                for i, h in enumerate(history):
                    print(f"[{i}] {h}")
                continue

            # parse command with shlex
            parts = shlex.split(raw)
            fn_name = parts[0]
            args, kwargs = [], []

            for token in parts[1:]:
                if "=" in token and not token.startswith(("'", '"')):  # keyword arg
                    k, v = token.split("=", 1)
                    kwargs.append((k, v))
                elif token in ("True", "False"):  # booleans
                    args.append(token == "True")
                else:
                    args.append(token)

            # execute function
            if fn_name in globals():
                try:
                    fn = globals()[fn_name]
                    kw = {k: v for k, v in kwargs}
                    result = fn(*args, **kw)
                    results[f"{fn_name}_{command_id}"] = result
                    print(result)
                    history.append(raw)
                    command_id += 1
                except Exception as e:
                    print(f"[ERROR] {e}")
            else:
                print(f"[ERROR] Unknown function: {fn_name}")

        except KeyboardInterrupt:
            print("\n[TERMINAL] Exit requested with Ctrl+C")
            break
        except EOFError:
            print("\n[TERMINAL] Exit requested (EOF)")
            break

    return results
