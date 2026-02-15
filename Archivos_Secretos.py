import tkinter as tk
from tkinter import messagebox
import json
import os
import webbrowser

# -----------------------
# Config UI (dark)
# -----------------------
BG = "#0f0f0f"
FG = "#eaeaea"
ACCENT = "#1f6feb"
ENTRY_BG = "#141414"
ENTRY_FG = "#ffffff"
CARD_BG = "#121212"
BORDER = "#2a2a2a"

# -----------------------
# Load JSON from repo
# -----------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "expedientes.json")


def load_vault():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Missing JSON: {DATA_PATH}")
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


VAULT = load_vault()
MASTER_TOKEN = VAULT.get("master_token", "EXP00.NODE")
NODES = VAULT.get("items", [])


# -----------------------
# Case Window (dossier style)
# -----------------------
def open_case_window(parent, node):
    win = tk.Toplevel(parent)
    win.title(node.get("id", "EXPEDIENTE"))
    win.geometry("860x560")
    win.configure(bg=BG)
    win.resizable(False, False)

    container = tk.Frame(win, bg=BG)
    container.pack(expand=True, fill="both", padx=26, pady=22)

    def header_row(label, value):
        row = tk.Frame(container, bg=BG)
        row.pack(anchor="w", pady=2)
        tk.Label(row, text=f"{label}:", bg=BG, fg=FG,
                 font=("Segoe UI", 12, "bold")).pack(side="left")
        tk.Label(row, text=f" {value}", bg=BG, fg="#7bb6ff",
                 font=("Segoe UI", 12, "bold")).pack(side="left")

    header_row("Registro", node.get("registro", "—"))
    header_row("Clasificación", node.get("clasificacion", "—"))
    header_row("Estado", node.get("estado", "—"))

    tk.Label(container, text="", bg=BG).pack(anchor="w", pady=6)

    def section(title, lines, height_hint=10):
        if not lines:
            return
        tk.Label(container, text=title, bg=BG, fg=FG,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(8, 6))
        box = tk.Text(
            container,
            bg=ENTRY_BG, fg=FG, insertbackground=FG,
            relief="flat", font=("Consolas", 11),
            wrap="word", height=height_hint
        )
        box.pack(fill="x", expand=False)

        # lines can be list[str] or single str
        if isinstance(lines, str):
            text = lines.strip()
        else:
            text = "\n\n".join([l.strip() for l in lines if str(l).strip()])

        box.insert("1.0", text if text else "(Sin contenido)")
        box.configure(state="disabled")

    section("Descripción resumida:", node.get("descripcion_resumida", []), height_hint=12)
    section("Conclusión del archivo:", node.get("conclusion", []), height_hint=6)

    links = node.get("links", [])
    if links:
        links_frame = tk.Frame(container, bg=BG)
        links_frame.pack(anchor="w", pady=(12, 0))
        tk.Label(links_frame, text="Links:", bg=BG, fg="#9a9a9a",
                 font=("Segoe UI", 10, "bold")).pack(side="left")

        for link in links[:6]:
            label = link.get("label", "Open")
            url = link.get("url", "")
            if not url:
                continue
            tk.Button(
                links_frame, text=label,
                command=lambda u=url: webbrowser.open(u),
                bg=CARD_BG, fg=FG,
                activebackground=CARD_BG, activeforeground=FG,
                relief="flat", padx=10, pady=4
            ).pack(side="left", padx=6)


# -----------------------
# Vault Window (list + key)
# -----------------------
def open_vault_window(parent):
    vault = tk.Toplevel(parent)
    vault.title("NODE VAULT")
    vault.geometry("760x420")
    vault.configure(bg=BG)
    vault.resizable(False, False)

    container = tk.Frame(vault, bg=BG)
    container.pack(expand=True, fill="both", padx=24, pady=20)

    tk.Label(container, text="NODE VAULT", bg=BG, fg=FG,
             font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(0, 6))

    tk.Label(container,
             text="Select a node and enter its access key (the node id) to open it.",
             bg=BG, fg="#9a9a9a", font=("Segoe UI", 10)
             ).pack(anchor="w", pady=(0, 16))

    card = tk.Frame(container, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1)
    card.pack(fill="both", expand=True)

    left = tk.Frame(card, bg=CARD_BG)
    left.pack(side="left", fill="both", expand=True, padx=14, pady=14)

    right = tk.Frame(card, bg=CARD_BG)
    right.pack(side="right", fill="y", padx=14, pady=14)

    tk.Label(left, text="Nodes", bg=CARD_BG, fg=FG,
             font=("Segoe UI", 11, "bold")).pack(anchor="w")

    listbox = tk.Listbox(
        left,
        bg=ENTRY_BG, fg=FG,
        selectbackground="#2b2b2b",
        selectforeground=FG,
        highlightthickness=0,
        relief="flat",
        font=("Segoe UI", 11),
        height=12
    )
    listbox.pack(fill="both", expand=True, pady=(8, 0))

    # Show: ID only (clean). You can change to "ID — Registro"
    for n in NODES:
        node_id = n.get("id", "UNKNOWN")
        listbox.insert("end", node_id)

    tk.Label(right, text="Access key", bg=CARD_BG, fg=FG,
             font=("Segoe UI", 11, "bold")).pack(anchor="w")

    key_var = tk.StringVar()
    key_entry = tk.Entry(
        right,
        textvariable=key_var,
        show="•",
        bg=ENTRY_BG, fg=ENTRY_FG,
        insertbackground=FG,
        relief="flat",
        font=("Segoe UI", 12),
        width=28
    )
    key_entry.pack(anchor="w", pady=(8, 12), ipady=6)
    key_entry.focus_set()

    tk.Label(
        right,
        text="Tip: key == node id\nExample: EXP06.NON_LINEAR_ROUTE",
        bg=CARD_BG, fg="#9a9a9a",
        font=("Segoe UI", 9),
        justify="left"
    ).pack(anchor="w", pady=(0, 12))

    def get_selected_node():
        sel = listbox.curselection()
        if not sel:
            return None
        return NODES[sel[0]]

    def open_node(event=None):
        node = get_selected_node()
        if not node:
            messagebox.showwarning("NODE VAULT", "Select a node first.")
            return

        entered = key_var.get().strip()
        if not entered:
            messagebox.showwarning("NODE VAULT", "Enter the access key.")
            return

        if entered != node.get("access_key", ""):
            messagebox.showerror("ACCESS DENIED", "Invalid access key for this node.")
            return

        open_case_window(vault, node)

    tk.Button(
        right,
        text="OPEN",
        command=open_node,
        bg=ACCENT, fg="#ffffff",
        activebackground=ACCENT, activeforeground="#ffffff",
        relief="flat",
        font=("Segoe UI", 11, "bold"),
        padx=14, pady=6
    ).pack(anchor="w", pady=(0, 8))

    listbox.bind("<Double-Button-1>", open_node)
    vault.bind("<Return>", open_node)

    if NODES:
        listbox.selection_set(0)
        listbox.activate(0)

    return vault


# -----------------------
# Login Window
# -----------------------
def main():
    root = tk.Tk()
    root.title("ACCESS NODE")
    root.geometry("420x220")
    root.configure(bg=BG)
    root.resizable(False, False)

    # Center window
    root.update_idletasks()
    w, h = 420, 220
    x = (root.winfo_screenwidth() // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)
    root.geometry(f"{w}x{h}+{x}+{y}")

    container = tk.Frame(root, bg=BG)
    container.pack(expand=True, fill="both", padx=24, pady=20)

    tk.Label(container, text="ACCESS NODE", bg=BG, fg=FG,
             font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(0, 12))

    tk.Label(container, text="Entry token", bg=BG, fg=FG,
             font=("Segoe UI", 11)).pack(anchor="w")

    token_var = tk.StringVar()
    entry = tk.Entry(
        container,
        textvariable=token_var,
        show="•",
        bg=ENTRY_BG, fg=ENTRY_FG,
        insertbackground=FG,
        relief="flat",
        font=("Segoe UI", 12)
    )
    entry.pack(anchor="w", fill="x", pady=(6, 14), ipady=6)
    entry.focus_set()

    def on_verify(event=None):
        token = token_var.get().strip()
        if not token:
            messagebox.showwarning("ACCESS NODE", "Please enter a token.")
            return
        if token != MASTER_TOKEN:
            messagebox.showerror("ACCESS DENIED", "Invalid token.")
            return

        root.withdraw()
        vault = open_vault_window(root)

        def on_vault_close():
            vault.destroy()
            root.deiconify()
            token_var.set("")
            entry.focus_set()

        vault.protocol("WM_DELETE_WINDOW", on_vault_close)

    tk.Button(
        container,
        text="VERIFY",
        command=on_verify,
        bg=ACCENT, fg="#ffffff",
        activebackground=ACCENT, activeforeground="#ffffff",
        relief="flat",
        font=("Segoe UI", 11, "bold"),
        padx=14, pady=6
    ).pack(anchor="w")

    root.bind("<Return>", on_verify)
    root.mainloop()


if __name__ == "__main__":
    main()
