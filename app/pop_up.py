from tkinter import *
from tkinter import ttk


class PopUp(Tk):

    def __init__(self, master):
        self.val = 0
        self.master = master
        self.win = Toplevel(self.master)

        self.input = Entry(self.win, width=10)
        self.input.grid(row=0, column=0)

        self.btn = Button(self.win, text="Enter", command=self.show)
        self.btn.grid(row=1, column=0)

    def show(self):
        try:
            self.val = int(self.input.get())
            self.win.destroy()
        except Exception:
            pass