from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image

BG_GRAY = "#ABB2B9"  # Gray Color
BG_COLOR = "#17202A"  # BG Color
TEXT_COLOR = "#EAECEE"  # Text Color
FONT = "Arial"  # Font

EYE_VISIBLE_IMG = Image.open("Images/eye.png")  # Image for visible eye
EYE_INVISIBLE_IMG = Image.open("Images/eye-invisible.png")  # Image for visible eye


class LoginGUI:
    PASSWORD_SHOWN = False  # Is password currently shown
    """
    Init variables setting parent to user_form and setting up the GUI for this window
    """
    def __init__(self, user_form):
        self.parent = user_form
        self.Window = user_form.Window
        self.show_login_GUI()

    """
    Create the login GUI, callbacks, and retrieve login information if need be
    """
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
        self.user_textbox = ttk.Entry(self.username_frame, textvariable=self.user_text,
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
        self.login_error = Label(self.login_frame, textvariable=self.login_error_text,
                                 font=(FONT, 12), fg="#FF0000")

        self.login_error.place(relx=0.5,
                               rely=0.3, anchor=CENTER)

        # create a Continue Button
        # along with action
        self.login_button = ttk.Button(self.login_frame,
                                       text="LOGIN",
                                       style='Accent.TButton',
                                       command=lambda: self.try_login(self.user_text.get(), self.password_text.get()))

        self.login_button.place(relx=0.5,
                                rely=0.75, anchor=CENTER)

        self.register_button = ttk.Button(self.login_frame,
                                          text="Register",
                                          style='TButton',
                                          command=lambda: self.parent.goto_register())

        self.register_button.place(relx=0.25,
                                   rely=0.75, anchor=CENTER)

        # set the focus of the cursor
        self.user_textbox.focus()

        self.retrieve_login_info()

    """
    Try logging in with the info in the entries
    """
    def try_login(self, username, password):
        print(username)

        # get the result of success or fail and error message back from login attempt
        login_result, error_msg = self.parent.socket_manager.try_login(username, password)
        # if success remove this window and show the chat window and save the login info to text
        if login_result:
            self.parent.set_login_info(username, password)
            self.remove_login_GUI()
            self.parent.show_chat()
        # if failure set the error message to the label
        else:
            self.login_error_text.set(error_msg)

    """
    Destroy the login frame
    """
    def remove_login_GUI(self):
        self.login_frame.destroy()

    """
    Check for any saved login information from a previous session
    """
    def retrieve_login_info(self):
        try:
            f = open("userinfo.txt", "r")
            info = f.read().split(":")
            self.user_text.set(info[0])
            self.password_text.set(info[1])
        except IOError:
            pass

    """
    Called when a user clicks the eye button next to password, shows or hides the password
    """
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
