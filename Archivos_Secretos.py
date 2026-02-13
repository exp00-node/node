import tkinter as tk
from tkinter import messagebox
import json
import os
import webbrowser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "expedientes.json")

def load_vault():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

VAULT = load_vault()
MASTER_TOKEN = VAULT.get("master_token", "EXP00.NODE")
NODES = VAULT.get("items", [])

def open_case_window(parent, node):
    win = tk.Toplevel(parent)
    win.title(node.get("id", "CASE"))
    win.geometry("820x520")
    win.configure(bg=BG)
    win.resizable(False, False)

    container = tk.Frame(win, bg=BG)
    container.pack(expand=True, fill="both", padx=24, pady=20)

    title = node.get("title") or node.get("id") or "UNNAMED"
    tk.Label(container, text=title, bg=BG, fg=FG, font=("Segoe UI", 18, "bold")).pack(anchor="w")

    summary = node.get("summary", "").strip()
    if summary:
        tk.Label(container, text=summary, bg=BG, fg="#9a9a9a", font=("Segoe UI", 10), wraplength=760, justify="left").pack(anchor="w", pady=(6, 12))

    # Caja de texto (solo lectura)
    txt = tk.Text(container, bg=ENTRY_BG, fg=FG, insertbackground=FG, relief="flat",
                  font=("Consolas", 11), wrap="word", height=16)
    txt.pack(fill="both", expand=True)

    body = node.get("body", "").strip()
    if not body:
        body = "(No content)"
    txt.insert("1.0", body)
    txt.configure(state="disabled")

    # Links (si existen)
    links = node.get("links", [])
    if links:
        links_frame = tk.Frame(container, bg=BG)
        links_frame.pack(anchor="w", pady=(12, 0))
        tk.Label(links_frame, text="Links:", bg=BG, fg="#9a9a9a", font=("Segoe UI", 10, "bold")).pack(side="left")

        for link in links[:5]:  # límite por limpieza visual
            label = link.get("label", "Open")
            url = link.get("url", "")
            if not url:
                continue
            b = tk.Button(
                links_frame, text=label,
                command=lambda u=url: webbrowser.open(u),
                bg=CARD_BG, fg=FG,
                activebackground=CARD_BG, activeforeground=FG,
                relief="flat", padx=10, pady=4
            )
            b.pack(side="left", padx=6)

# --- Config UI ---
BG = "#0f0f0f"
FG = "#eaeaea"
ACCENT = "#1f6feb"
ENTRY_BG = "#141414"
ENTRY_FG = "#ffffff"
CARD_BG = "#121212"
BORDER = "#2a2a2a"

# --- 1) TOKEN PRINCIPAL (login) ---
MASTER_TOKEN = "EXP00.NODE"   # clave principal

# --- 2) "ARCHIVOS" + CLAVES (simulado) ---
# Luego esto lo leeremos de un JSON.
NODES = [
    {"name": "PERSISTENT_PRESENCE", "access_key": "EXP01.PERSISTENT_PRESENCE"},
    {"name": "ABNORMAL_EXIT", "access_key": "EXP02.ABNORMAL_EXIT"},
    {"name": "NULL_RECORD", "access_key": "EXP03.NULL_RECORD"},
    {"name": "FATAL_SIGNAL", "access_key": "EXP04.FATAL_SIGNAL"},
    {"name": "UNREGISTERED_PRESENCE", "access_key": "EXP05.UNREGISTERED_PRESENCE"},
    {"name": "NON_LINEAR_ROUTE", "access_key": "EXP06.NON_LINEAR_ROUTE"},
    {"name": "LAST_CONTACT", "access_key": "EXP08.LAST_CONTACT"},
]

def open_vault_window(parent):
    """Ventana 2: Explorer / Vault."""
    vault = tk.Toplevel(parent)
    vault.title("NODE VAULT")
    vault.geometry("760x420")
    vault.configure(bg=BG)
    vault.resizable(False, False)

    # Layout principal
    container = tk.Frame(vault, bg=BG)
    container.pack(expand=True, fill="both", padx=24, pady=20)

    header = tk.Label(
        container,
        text="NODE VAULT",
        bg=BG, fg=FG,
        font=("Segoe UI", 18, "bold"),
    )
    header.pack(anchor="w", pady=(0, 6))

    sub = tk.Label(
        container,
        text="Select a node and enter its access key to open details.",
        bg=BG, fg="#9a9a9a",
        font=("Segoe UI", 10),
    )
    sub.pack(anchor="w", pady=(0, 16))

    # Card
    card = tk.Frame(container, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1)
    card.pack(fill="both", expand=True)

    left = tk.Frame(card, bg=CARD_BG)
    left.pack(side="left", fill="both", expand=True, padx=14, pady=14)

    right = tk.Frame(card, bg=CARD_BG)
    right.pack(side="right", fill="y", padx=14, pady=14)

    # Lista de nodos
    tk.Label(left, text="Nodes", bg=CARD_BG, fg=FG, font=("Segoe UI", 11, "bold")).pack(anchor="w")

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

    for n in NODES:
        display_title = n.get("title") or n.get("name") or "UNNAMED"
        display_name = n.get("name") or "UNKNOWN.NODE"
        listbox.insert("end", f"{display_name}  —  {display_title}")

    # Panel derecho: clave
    tk.Label(right, text="Access key", bg=CARD_BG, fg=FG, font=("Segoe UI", 11, "bold")).pack(anchor="w")

    key_var = tk.StringVar()
    key_entry = tk.Entry(
        right,
        textvariable=key_var,
        show="•",
        bg=ENTRY_BG, fg=ENTRY_FG,
        insertbackground=FG,
        relief="flat",
        font=("Segoe UI", 12),
        width=24
    )
    key_entry.pack(anchor="w", pady=(8, 12), ipady=6)

    info = tk.Label(
        right,
        text="Tip: keys match the node id.\nExample: EXP00.NODE",
        bg=CARD_BG, fg="#9a9a9a",
        font=("Segoe UI", 9),
        justify="left"
    )
    info.pack(anchor="w", pady=(0, 12))

    def get_selected_node():
        sel = listbox.curselection()
        if not sel:
            return None
        idx = sel[0]
        return NODES[idx]

    def open_node(event=None):
        node = get_selected_node()

        if "access_key" not in node or not node["access_key"]:
            messagebox.showerror("NODE ERROR", "This node has no access_key configured.")
            return

        if not node:
            messagebox.showwarning("NODE VAULT", "Select a node first.")
            return

        entered = key_var.get().strip()
        if not entered:
            messagebox.showwarning("NODE VAULT", "Enter the access key.")
            return

        if entered != node["access_key"]:
            messagebox.showerror("ACCESS DENIED", "Invalid access key for this node.")
            return

        # Aquí luego abrirás la ventana real del nodo (detalles, archivos, etc.)
        display_title = node.get("title") or node.get("name") or "UNNAMED"
        display_name = node.get("name") or "UNKNOWN.NODE"
        open_case_window(vault, node)
    open_btn = tk.Button(
        right,
        text="OPEN",
        command=open_node,
        bg=ACCENT, fg="#ffffff",
        activebackground=ACCENT, activeforeground="#ffffff",
        relief="flat",
        font=("Segoe UI", 11, "bold"),
        padx=14, pady=6
    )
    open_btn.pack(anchor="w", pady=(0, 8))

    # Doble click en lista abre (si clave correcta)
    listbox.bind("<Double-Button-1>", open_node)
    vault.bind("<Return>", open_node)

    # selección por defecto
    if NODES:
        listbox.selection_set(0)
        listbox.activate(0)
        key_entry.focus_set()

    return vault


def main():
    root = tk.Tk()
    root.title("ACCESS NODE")
    root.geometry("420x220")
    root.configure(bg=BG)
    root.resizable(False, False)

    # Centrar
    root.update_idletasks()
    w, h = 420, 220
    x = (root.winfo_screenwidth() // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)
    root.geometry(f"{w}x{h}+{x}+{y}")

    container = tk.Frame(root, bg=BG)
    container.pack(expand=True, fill="both", padx=24, pady=20)

    tk.Label(container, text="ACCESS NODE", bg=BG, fg=FG, font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(0, 12))
    tk.Label(container, text="Entry token", bg=BG, fg=FG, font=("Segoe UI", 11)).pack(anchor="w")

    token_var = tk.StringVar()
    entry = tk.Entry(
        container,
        textvariable=token_var,
        show="•",
        bg=ENTRY_BG, fg=ENTRY_FG,
        insertbackground=FG,
        relief="flat",
        font=("Segoe UI", 12),
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

        # Acceso correcto: abrir vault y ocultar login
        root.withdraw()
        vault = open_vault_window(root)

        # Si cierras vault, vuelve a mostrar login (o cierra app)
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
        padx=14, pady=6,
    ).pack(anchor="w")

    root.bind("<Return>", on_verify)

    root.mainloop()


if __name__ == "__main__":
    main()