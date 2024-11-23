import tkinter as tk
from tkinter import simpledialog


def Selector(lst):
    def on_select():
        nonlocal selected_items
        selected_items = [lst[i] for i in lb.curselection()]
        root.destroy()
    
    selected_items = []
    
    root = tk.Tk()
    root.title("Multi-Select List")
    root.geometry("300x300")

    lb = tk.Listbox(root, selectmode=tk.MULTIPLE)
    for item in lst:
        lb.insert(tk.END, item)
    lb.pack(padx=10, pady=10)

    select_button = tk.Button(root, text="Select", command=on_select)
    select_button.pack(pady=10)

    root.mainloop()
    
    return selected_items