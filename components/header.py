# components/header.py
import customtkinter as CTk

class Header(CTk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        style = CTk.CTkStyle()
        style.configure('Header.TLabel', background='#2d5a27', foreground='white', font=('Arial', 16, 'bold'), padding=10)
        
        header_label = CTk.CTkLabel(self, text="DW Youtube", style='Header.TLabel', anchor="center")
        header_label.pack(fill=CTk.X, expand=True)