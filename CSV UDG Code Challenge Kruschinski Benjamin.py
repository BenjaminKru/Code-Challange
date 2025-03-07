import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd

root = tk.Tk()
root.title("CSV Einleser")
root.geometry("1200x800")
frame = tk.Frame(root)

frame.pack(fill=tk.BOTH, expand=True)
tree_scroll_y = ttk.Scrollbar(frame, orient="vertical")
tree_scroll_x = ttk.Scrollbar(frame, orient="horizontal")

tree = ttk.Treeview(frame, yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
tree_scroll_y.config(command=tree.yview)
tree_scroll_x.config(command=tree.xview)

tree.pack(side="left", fill=tk.BOTH, expand=True)
tree_scroll_y.pack(side="right", fill="y")
tree_scroll_x.pack(side="bottom", fill="x")

style = ttk.Style()
style.configure("Treeview", rowheight=30)

df = pd.DataFrame()

def csv_laden():
    global df
    dateipfad = filedialog.askopenfilename(filetypes=[("CSV-Dateien", "*.csv")])
    if not dateipfad:
        return
    try:
        df = pd.read_csv(dateipfad, sep=None, engine="python", on_bad_lines="skip", header=None)
        df.columns = [f"Spalte {i+1}" for i in range(len(df.columns))]
        tabelle_aktualisieren()
    except Exception as e:
        messagebox.showerror("Fehler", "Fehler beim Laden der CSV-Datei.")

def tabelle_aktualisieren():
    tree.delete(*tree.get_children())

    if df.empty:
        return

    tree["columns"] = df.columns.tolist()
    for spalte in df.columns:
        tree.heading(spalte, text=spalte)
        tree.column(spalte, anchor=tk.W, width=100)

    for _, zeile in df.iterrows():
        tree.insert("", "end", values=zeile.tolist())

    spalten_breite_anpassen()

def spalten_breite_anpassen():
    for spalte in df.columns:
        max_laenge_wert = df[spalte].astype(str).map(len).max()
        max_laenge = max(max_laenge_wert, len(spalte))
        tree.column(spalte, width=max_laenge * 10)

btn_load = tk.Button(root, text="CSV laden", command=csv_laden)
btn_load.pack()

def zeile_bearbeiten():
    auswahl = tree.selection()
    if not auswahl:
        messagebox.showwarning("Warnung", "Bitte eine Zeile auswählen!")
        return

    zeile = tree.item(auswahl[0])
    werte = zeile["values"]

    bearbeiten_fenster = tk.Toplevel(root)
    bearbeiten_fenster.title("Zeile bearbeiten")

    eingaben = []
    for i, spaltenname in enumerate(df.columns):
        tk.Label(bearbeiten_fenster, text=spaltenname).grid(row=i, column=0)
        eingabe = tk.Entry(bearbeiten_fenster)
        eingabe.grid(row=i, column=1)
        eingabe.insert(0, werte[i])
        eingaben.append(eingabe)

    def speichern():
        index = df.index[df[df.columns[0]] == werte[0]].tolist()
        if index:
            for i, spaltenname in enumerate(df.columns):
                df.loc[index[0], spaltenname] = eingaben[i].get()
            tabelle_aktualisieren()
        bearbeiten_fenster.destroy()

    tk.Button(bearbeiten_fenster, text="Speichern", command=speichern).grid(row=len(df.columns), column=1)

btn_edit = tk.Button(root, text="Zeile bearbeiten", command=zeile_bearbeiten)
btn_edit.pack()

def zeile_hinzufuegen():
    hinzufuegen_fenster = tk.Toplevel(root)
    hinzufuegen_fenster.title("Neue Zeile hinzufügen")

    eingaben = []
    for i, spaltenname in enumerate(df.columns):
        tk.Label(hinzufuegen_fenster, text=spaltenname).grid(row=i, column=0)
        eingabe = tk.Entry(hinzufuegen_fenster)
        eingabe.grid(row=i, column=1)
        eingaben.append(eingabe)

    def speichern_zeile():
        global df
        neue_daten = {df.columns[i]: eingaben[i].get() for i in range(len(df.columns))}
        df = pd.concat([df, pd.DataFrame([neue_daten])], ignore_index=True)
        tabelle_aktualisieren()
        hinzufuegen_fenster.destroy()

    tk.Button(hinzufuegen_fenster, text="Hinzufügen", command=speichern_zeile).grid(row=len(df.columns), column=1)

btn_add = tk.Button(root, text="Neue Zeile hinzufügen", command=zeile_hinzufuegen)
btn_add.pack()

def csv_speichern():
    dateipfad = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV-Dateien", "*.csv")])
    if dateipfad:
        df.to_csv(dateipfad, index=False)
        messagebox.showinfo("Erfolg", "Datei gespeichert!")

btn_save = tk.Button(root, text="CSV speichern", command=csv_speichern)
btn_save.pack()

btn_exit = tk.Button(root, text="Beenden", command=root.destroy)
btn_exit.pack()

root.mainloop()