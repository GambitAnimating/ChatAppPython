from tkinter import *
from tkinter import ttk

BG_GRAY = "#ABB2B9"
BG_COLOR = "#17202A"
TEXT_COLOR = "#EAECEE"
FONT = "Arial"
font_dict = {}

class ChatGUI:

    def __init__(self, user_form):
        self.parent = user_form
        self.Window = user_form.Window
        self.show_login_GUI()
        self.Window.bind("<Configure>", self.window_resized)
        self.parent.socket_manager.start_chat()

    def show_login_GUI(self):
        # set the title
        self.Window.title("Chatroom")

        # get screen width and height
        ws = self.Window.winfo_screenwidth()  # width of the screen
        hs = self.Window.winfo_screenheight()  # height of the screen
        # set the dimensions of the screen
        # and where it is placed
        self.Window.geometry('800x400')
        #self.Window.geometry('%dx%d+%d+%d' % (ws, hs, 0, 0))
        self.Window.update()

        self.Window.resizable(width=False,
                              height=False)

        # login window
        self.chat_frame = ttk.Frame(self.Window)
        self.chat_frame.place(relheight=1, relwidth=1)

        # create a Label
        self.login_help_label = Label(self.chat_frame,
                                      text="Please Login or Register to continue",
                                      font="Helvetica 14 bold")

        self.login_help_label.place(relheight=0.15,
                                    relx=0.5,
                                    rely=0.15, anchor=CENTER)

        # CREATE NAME FIELD
        self.username_frame = Frame(self.chat_frame)
        self.username_frame.place(relheight=.1, relwidth=1, relx=.5, rely=.4, anchor=CENTER)

        self.user_label = Label(self.username_frame,
                                text="Username: ",
                                font=(FONT, 16))

        # Add desired size to dict
        font_dict[self.user_label] = .02

        self.user_label.place(relheight=1,
                              relx=0.15,
                              rely=.5, anchor=CENTER)

        self.user_text = StringVar()
        self.user_textbox = Entry(self.username_frame, textvariable=self.user_text,
                                  font=(FONT, 14))
        # Add desired size to dict
        font_dict[self.user_textbox] = .02

        self.user_textbox.place(relwidth=0.5,
                                relheight=1,
                                relx=0.725,
                                rely=.5, anchor=E)

        # CREATE PASSWORD FIELD
        self.password_frame = Frame(self.chat_frame)
        self.password_frame.place(relheight=.1, relwidth=1, relx=.5, rely=.55, anchor=CENTER)

        self.password_label = Label(self.password_frame,
                                    text="Password: ",
                                    font=(FONT, 14))

        self.password_label.place(relheight=1,
                                  relx=0.15,
                                  rely=.5, anchor=CENTER)

        self.password_text = StringVar()
        self.password_textbox = Entry(self.password_frame, textvariable=self.password_text, show="*",
                                      font=(FONT, 14))

        # CREATE CHAT FIELD
        self.chat_messagebox_frame = Frame(self.chat_frame)
        self.chat_messagebox_frame.place(relheight=.1, relwidth=1, relx=.5, rely=1, anchor=S)

        self.chat_text = StringVar()
        self.chat_messagebox = Entry(self.chat_messagebox_frame, textvariable=self.chat_text,
                                  font=(FONT, 14))
        # Add desired size to dict
        font_dict[self.chat_messagebox] = .022

        self.chat_messagebox.place(relwidth=.8,
                                relheight=1,
                                relx=.5,
                                rely=1, anchor=S)

        self.textCons = Text(self.Window,
                             width=20,
                             height=2,
                             bg="#17202A",
                             fg="#EAECEE",
                             font="Helvetica 14",
                             padx=5,
                             pady=5)

        self.textCons.place(relheight=0.85,
                            relwidth=.85,relx = .5,
                            rely=.85, anchor=S)

        self.textCons.config(cursor="arrow")

        # create a scroll bar
        scrollbar = Scrollbar(self.textCons)

        # place the scroll bar
        # into the gui window
        scrollbar.place(relheight=1.01,
                        relx=1, rely=1.003, anchor=S)
        self.textCons.config(yscrollcommand=scrollbar.set)

        scrollbar.config(command=self.textCons.yview)
        self.textCons.config(state=DISABLED)

        self.chat_messagebox.bind("<Return>", lambda event: self.send_msg(self.chat_text.get()))


        # set the focus of the cursor
        self.user_textbox.focus()

    def send_msg(self, message):
        print(message)
        self.parent.socket_manager.send_chat(message)

    def got_message(self, message):
        self.textCons.config(state=NORMAL)
        self.textCons.insert(END,
                             message)

        self.textCons.config(state=DISABLED)
        self.textCons.see(END)
        self.chat_messagebox.delete(0, END)

    def hide_chat_GUI(self):
        self.chat_frame.place_forget()

    def remove_chat_GUI(self):
        self.chat_frame.destroy()

    def window_resized(self, event):
       for widget, value in font_dict.items():
           aspect_ratio = self.Window.winfo_height() / self.Window.winfo_width()
           widget.configure(font=(FONT, int(value * self.Window.winfo_width())))
