from tkinter import *
from tkinter import ttk


class UserInfo(Tk):

    def __init__(self, master):
        self.age = ['User', 'User']
        self.sex = ['User', 'User']
        self.height = ['User', 'User']
        self.weight = ['User', 'User']
        self.__options = ["Male", "Female"]
        self.__selected1 = StringVar()
        self.__selected2 = StringVar()
        self.master = master
        self.win = Toplevel(self.master)
        self.win.attributes("-alpha", 1)
        self.win.resizable(0, 0)

        self.lab = Label(self.win, text="Person 1", font=("default", 10, 'bold'))
        self.lab.grid(row=0, column=1)
        self.lab1 = Label(self.win, text="Person 2", font=("default", 10, 'bold'))
        self.lab1.grid(row=0, column=2)

        # Name
        self.age = Label(self.win, text="Age", font=("default", 10))
        self.age.grid(row=1, column=0)
        self.age_entr = ttk.Entry(self.win, font=("default", 10), width=13)
        self.age_entr.grid(row=1, column=1)

        self.age_entr1 = ttk.Entry(self.win, font=("default", 10), width=13)
        self.age_entr1.grid(row=1, column=2)

        # Sex
        self.age = Label(self.win, text="Age", font=("default", 10))
        self.age.grid(row=2, column=0)
        self.sex_menu = ttk.Combobox(self.win, value=self.__options,
                                     textvariable=self.__selected1)
        self.sex_menu.current(0)
        self.sex_menu.config(state="readonly", width=11)
        self.sex_menu.bind("<<ComboboxSelected>>")
        self.sex_menu.grid(row=2, column=1)

        self.sex_menu1 = ttk.Combobox(self.win, value=self.__options,
                                     textvariable=self.__selected2)
        self.sex_menu1.current(0)
        self.sex_menu1.config(state="readonly", width=11)
        self.sex_menu1.bind("<<ComboboxSelected>>")
        self.sex_menu1.grid(row=2, column=2)

        # Height
        self.height = Label(self.win, text="Height", font=("default", 10))
        self.height.grid(row=3, column=0)
        self.height_entr = ttk.Entry(self.win, font=("default", 10), width=13)
        self.height_entr.grid(row=3, column=1)

        self.height_entr1 = ttk.Entry(self.win, font=("default", 10), width=13)
        self.height_entr1.grid(row=3, column=2)


        # Weight
        self.weight = Label(self.win, text="Weight", font=("default", 10))
        self.weight.grid(row=4, column=0)
        self.weight_entr = ttk.Entry(self.win, font=("default", 10), width=13)
        self.weight_entr.grid(row=4, column=1)

        self.weight_entr1 = ttk.Entry(self.win, font=("default", 10), width=13)
        self.weight_entr1.grid(row=4, column=2)

        # Save button
        self.save_btn = ttk.Button(self.win,
                                   text="Enter", command=self.save_info)
        self.save_btn.grid(row=5, column=1, columnspan=2)

    def save_info(self):
        try:
            self.age = [self.age_entr.get(), self.age_entr1.get()]
            sex1 = self.__selected1.get()
            sex2 = self.__selected2.get()
            self.sex = [sex1, sex2]
            self.height = [self.height_entr.get(), self.height_entr1.get()]
            self.weight = [self.weight_entr.get(), self.weight_entr1.get()]
            self.win.destroy()
        except Exception:
            print(self.age_entr.get())
