from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image

BG_GRAY = "#ABB2B9"
BG_COLOR = "#17202A"
TEXT_COLOR = "#EAECEE"
FONT = "Arial"

EYE_VISIBLE_IMG = Image.open("Images/eye.png")
EYE_INVISIBLE_IMG = Image.open("Images/eye-invisible.png")


class RegisterGUI:
    PASSWORD_SHOWN = False

    def __init__(self, user_form):
        self.parent = user_form
        self.Window = user_form.Window
        self.show_register_GUI()

    def show_register_GUI(self):
        # set the title
        self.Window.title("Register")
        self.Window.resizable(width=False,
                              height=False)
        self.Window.configure(width=400,
                              height=300)

        # login window
        self.register_frame = ttk.Frame(self.Window)
        self.register_frame.place(relheight=1, relwidth=1)

        # create a Label
        self.register_help_label = Label(self.register_frame,
                                         text="Please Register to continue",
                                         font="Helvetica 14 bold")

        self.register_help_label.place(relheight=0.15,
                                       relx=0.5,
                                       rely=0.1, anchor=CENTER)

        # CREATE NAME FIELD
        self.username_frame = Frame(self.register_frame)
        self.username_frame.place(relheight=.1, relwidth=1, relx=.5, rely=.3, anchor=CENTER)

        self.user_label = Label(self.username_frame,
                                text="Username: ",
                                font=(FONT, 14))

        self.user_label.place(relheight=1,
                              relx=0.15,
                              rely=.5, anchor=CENTER)

        self.user_text = StringVar()
        self.user_textbox = ttk.Entry(self.username_frame, textvariable=self.user_text,
                                  font=(FONT, 14))

        self.user_textbox.place(relwidth=0.5,
                                relheight=1,
                                relx=0.5,
                                rely=.5, anchor=CENTER)

        # CREATE EMAIL FIELD
        self.email_frame = Frame(self.register_frame)
        self.email_frame.place(relheight=.1, relwidth=1, relx=.5, rely=.45, anchor=CENTER)

        self.email_label = Label(self.email_frame,
                                 text="Email: ",
                                 font=(FONT, 14))

        self.email_label.place(relheight=1,
                               relx=0.15,
                               rely=.5, anchor=CENTER)

        self.email_text = StringVar()
        self.email_textbox = ttk.Entry(self.email_frame, textvariable=self.email_text,
                                   font=(FONT, 14))

        self.email_textbox.place(relwidth=0.5,
                                 relheight=1,
                                 relx=0.5,
                                 rely=.5, anchor=CENTER)

        # CREATE PASSWORD FIELD
        self.password_frame = Frame(self.register_frame)
        self.password_frame.place(relheight=.1, relwidth=1, relx=.5, rely=.6, anchor=CENTER)

        self.password_label = Label(self.password_frame,
                                    text="Password: ",
                                    font=(FONT, 14))

        self.password_label.place(relheight=1,
                                  relx=0.15,
                                  rely=.5, anchor=CENTER)

        self.password_text = StringVar()
        self.password_textbox = ttk.Entry(self.password_frame, textvariable=self.password_text, show="*",
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
        self.login_error = Label(self.register_frame, textvariable=self.login_error_text,
                                 font=(FONT, 12), fg="#FF0000")

        self.login_error.place(relx=0.5,
                               rely=0.2, anchor=CENTER)

        # create a Continue Button
        # along with action
        self.register_button = ttk.Button(self.register_frame,
                                      text="REGISTER",
                                      style='Accent.TButton',
                                      command=lambda: self.try_register(self.user_text.get(), self.email_text.get(),
                                                                        self.password_text.get()))

        self.register_button.place(relx=0.5,
                                   rely=0.75, anchor=CENTER)

        self.login_button = ttk.Button(self.register_frame,
                                      text="Login",
                                       style='TButton',
                                      command=lambda: self.parent.goto_login())

        self.login_button.place(relx=0.25,
                                   rely=0.75, anchor=CENTER)

        # set the focus of the cursor
        self.user_textbox.focus()

    def try_register(self, username, email, password):
        register_result, error_msg = self.parent.socket_manager.try_register(username, email, password)
        if register_result:
            self.parent.set_login_info(username, password)
            self.remove_register_GUI()
            self.parent.show_chat()
            print("Registered successfully")
        else:
            self.login_error_text.set(error_msg)

    def hide_register_GUI(self):
        self.register_frame.place_forget()

    def remove_register_GUI(self):
        self.register_frame.destroy()

    def show_hide_password(self):
        if self.PASSWORD_SHOWN:
            img = EYE_VISIBLE_IMG.resize((30, 30), Image.BILINEAR)
            self.password_textbox.configure(show="*")
        else:
            img = EYE_INVISIBLE_IMG.resize((30, 30), Image.BILINEAR)
            self.password_textbox.configure(show="")
        self.PASSWORD_SHOWN = not self.PASSWORD_SHOWN

        self.eyeImage = ImageTk.PhotoImage(img)
        self.show_hide_canvas.itemconfig(self.bgImage, image=self.eyeImage)
