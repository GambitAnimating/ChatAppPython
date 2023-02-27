from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image

BG_GRAY = "#ABB2B9"
BG_COLOR = "#17202A"
TEXT_COLOR = "#EAECEE"
FONT = "Arial"

EYE_VISIBLE_IMG = Image.open("Images/eye.png")
EYE_INVISIBLE_IMG = Image.open("Images/eye-invisible.png")


class LoginGUI:
    PASSWORD_SHOWN = False
    def __init__(self, user_form):
        self.parent = user_form
        self.Window = user_form.Window
        self.show_login_GUI()

    def show_login_GUI(self):
        # set the title
        self.Window.title("Login")
        self.Window.resizable(width=False,
                              height=False)
        self.Window.configure(width=400,
                              height=300)

        # login window
        self.login_frame = ttk.Frame(self.Window)
        self.login_frame.place(relheight=1, relwidth=1)

        # create a Label
        self.login_help_label = Label(self.login_frame,
                                      text="Please Login or Register to continue",
                                      font="Helvetica 14 bold")

        self.login_help_label.place(relheight=0.15,
                                    relx=0.5,
                                    rely=0.15, anchor=CENTER)

        # CREATE NAME FIELD
        self.username_frame = Frame(self.login_frame)
        self.username_frame.place(relheight=.1, relwidth=1, relx=.5, rely=.4, anchor=CENTER)

        self.user_label = Label(self.username_frame,
                                text="Username: ",
                                font=(FONT, 14))

        self.user_label.place(relheight=1,
                              relx=0.15,
                              rely=.5, anchor=CENTER)

        self.user_text = StringVar()
        self.user_textbox = Entry(self.username_frame, textvariable=self.user_text,
                                  font=(FONT, 14))

        self.user_textbox.place(relwidth=0.5,
                                relheight=1,
                                relx=0.5,
                                rely=.5, anchor=CENTER)

        # CREATE PASSWORD FIELD
        self.password_frame = Frame(self.login_frame)
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

        self.show_hide_canvas = Canvas(self.password_frame)
        self.show_hide_canvas.place(relwidth=0.1,
                                    relheight=1,
                                    relx=0.8,
                                    rely=.5, anchor=CENTER)

        img = EYE_VISIBLE_IMG.resize((30, 30), Image.BILINEAR)
        self.eyeImage = ImageTk.PhotoImage(img)
        self.bgImage = self.show_hide_canvas.create_image(20, 15, image=self.eyeImage)
        self.show_hide_canvas.bind("<Button-1>", lambda event: self.show_hide_password())

        self.password_textbox.place(relwidth=0.5,
                                    relheight=1,
                                    relx=0.5,
                                    rely=.5, anchor=CENTER)

        # create a error label
        self.login_error_text = StringVar()
        self.login_error = Label(self.login_frame, textvariable=self.login_error_text,
                                      font=(FONT, 12), fg="#FF0000")

        self.login_error.place(relx=0.5,
                                    rely=0.3, anchor=CENTER)

        # create a Continue Button
        # along with action
        self.login_button = Button(self.login_frame,
                                   text="LOGIN",
                                   font=(FONT, 14, "bold"),
                                   command=lambda: self.try_login(self.user_text.get(), self.password_text.get()))

        self.login_button.place(relx=0.5,
                                rely=0.75, anchor=CENTER)

        self.register_button = Button(self.login_frame,
                                   text="Register",
                                   font=(FONT, 8, "bold"),
                                   command=lambda: self.parent.goto_register())

        self.register_button.place(relx=0.25,
                                rely=0.75, anchor=CENTER)

        # set the focus of the cursor
        self.user_textbox.focus()

    def try_login(self, username, password):
        print(username)

        login_result, error_msg = self.parent.socket_manager.try_login(username, password)
        if login_result:
            self.remove_login_GUI()
            self.parent.show_chat()
        else:
            self.login_error_text.set(error_msg)

    def hide_login_GUI(self):
        self.login_frame.place_forget()

    def remove_login_GUI(self):
        self.login_frame.destroy()

    def show_hide_password(self):
        if self.PASSWORD_SHOWN:
            img = EYE_VISIBLE_IMG.resize((30, 30), Image.BILINEAR)
            self.password_textbox.configure(show="*")
        else:
            img = EYE_INVISIBLE_IMG.resize((30, 30), Image.BILINEAR)
            self.password_textbox.configure(show="")
        self.PASSWORD_SHOWN = not self.PASSWORD_SHOWN

        self.eyeImage = ImageTk.PhotoImage(img)
        self.show_hide_canvas.itemconfig(self.bgImage,image=self.eyeImage)
