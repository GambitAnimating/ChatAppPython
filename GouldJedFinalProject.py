import json
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import Tk

from login import LoginGUI
from register import RegisterGUI
from chat_form import ChatGUI
import socket

"""
Class for handling all the connection, sending, and receiving of the socket
"""


class SocketManager:
    client = socket.socket()  # create the socket

    port = 8080  # port number
    FORMAT = "utf-8"  # format of text

    connected = False  # variable determining if connected

    """
    Function for connecting to the remote server
    """

    def connect(self, gui):
        self.client.connect(('74.208.5.206', self.port))
        # Receive and print the "connection" message
        conf_msg = self.client.recv(1024).decode()
        print(conf_msg)
        self.connected = True
        # Set the GUI variable of SocketManager
        self.gui = gui

    """
    Function used by login.py to try logging in, called when the user presses the login button
    """

    def try_login(self, username, password):
        # The request send to the server featuring username and password
        response_json = {"type": "LOGIN", "username": username, "password": password}
        self.sendjson(self.client, response_json)

        # The response is got from the server, and it gives us a message of success or error and why
        try:
            # Call to actually receive the data
            response_data = self.recvjson(self.client)
            if response_data is None:
                return False, 'Connection Error'
            packet_type = response_data['type']

            # Check if the response was of type LOGIN (it should have been) and return the error if there is one
            if packet_type == 'LOGIN':
                return response_data['success'], response_data['error']
        except ConnectionResetError:
            print('ConnectionResetError')
            return False, 'Connection refused'

        return False, 'Unknown Error'

    """
    Function used by register.py to try registering, called when the user presses the register button
    """

    def try_register(self, username, email, password):
        # The request send to the server featuring all register details
        response_json = {"type": "REGISTER", "username": username, "email": email, "password": password}
        self.sendjson(self.client, response_json)

        try:
            # Call to actually receive the data
            response_data = self.recvjson(self.client)
            if response_data is None:
                return False, 'Connection Error'
            packet_type = response_data['type']

            # Check if the response was of type REGISTER (it should have been) and return the error if there is one
            if packet_type == 'REGISTER':
                return response_data['success'], response_data['error']

        except ConnectionResetError:
            print('ConnectionResetError')
            return False, 'Connection refused'

        return False, 'Unknown Error'

    """
    Function used by chat_form.py to setup the thread for receiving chat data
    """

    def start_chat(self):
        # the thread to receive messages
        rcv = threading.Thread(target=self.receive)
        rcv.start()

        # the packet to the server saying we joined the chat
        response_json = {"type": "JOINED_SERVER"}
        self.sendjson(self.client, response_json)

    """
    Function used by chat_form.py to actually send the chat messages
    """

    def send_chat(self, message):
        # the packet send to the server with what we want to chat
        response_json = {"type": "CHAT_MESSAGE", "message": message}
        self.sendjson(self.client, response_json)

    """
    Function used for receiving any incoming packets
    """

    def receive(self):
        while self.connected:
            try:
                response_data = self.recvjson(self.client)
                if response_data is None:
                    self.connected = False
                    break
                packet_type = response_data['type']

                # Check what type of packet it is and depending on that, change behavior as well as have our catches

                if packet_type == 'CHAT_MESSAGE':
                    self.gui.chat_GUI.got_message(response_data['message'])

                if packet_type == 'OLD_MESSAGES':
                    self.gui.chat_GUI.got_message(response_data['messages'])
            except ConnectionResetError:
                print('ConnectionResetError')
                self.connected = False
                break
            except KeyboardInterrupt:
                print("Application closed, close socket")
                self.connected = False
                break

        self.client.close()

    """
    Function for closing the socket
    """

    def close(self):
        self.connected = False
        self.client.close()

    """
    Function for sending the json data
    """

    @staticmethod
    def sendjson(conn, data):
        # Serialize data to Json formatted str
        response_json = json.dumps(data)
        # Get the length of that data in bytes
        header = len(response_json).to_bytes(4, 'big')
        # Send the packet to the server
        conn.sendall(header + response_json.encode())

    """
    Function for receiving the json data
    """

    @staticmethod
    def recvjson(conn):
        try:
            # get the header bytes size which is 4 bites because it's an int
            header = conn.recv(4)
            # If the header is empty, the connection has been closed
            if not header:
                print("The connection has been closed")
                return None

            # convert the header bytes to thew actual int
            json_length = int.from_bytes(header, 'big')
            print(json_length)
            message = b''  # the variable to hold the message in bytes
            while len(message) < json_length:
                # get a chunk of data as much as we can and if we cant get it all at once, try again on next loop
                chunk = conn.recv(json_length - len(message))
                print(chunk)
                if chunk == b'':
                    raise RuntimeError("Socket connection broken")
                # append the chunk to the message
                message += chunk
            # decode the message to json
            response_data = json.loads(message.decode())
            return response_data
        except OSError:
            print("OS Error")


"""
GUI class handles all GUI windows and functions
"""


class GUI:
    username = ""  # the username for client
    password = ""  # the password for client

    # constructor method
    def __init__(self):
        self.socket_manager = SocketManager()  # create an instance of the class
        # connect to the server
        self.socket_manager.connect(self)

        self.login_GUI, self.register_GUI, self.chat_GUI = None, None, None  # get the guis ready

        self.Window = Tk()  # create the window

        # setup theme settings
        self.Window.tk.call("source", "azure.tcl")
        self.Window.tk.call("set_theme", "dark")

        # add callback for window closing
        self.Window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.login_GUI = LoginGUI(self)

        self.Window.mainloop()

    """
    Changes the window to register view
    """
    def goto_register(self):
        self.register_GUI = RegisterGUI(self)

    """
    Changes the window to chat view
    """
    def show_chat(self):
        self.chat_GUI = ChatGUI(self)

    """
    Changes the window to login view
    """
    def goto_login(self):
        self.login_GUI = LoginGUI(self)

    """
    Noting login info so we can save it later
    """
    def set_login_info(self, username, password):
        self.username = username
        self.password = password

    """
    Try saving the login info to a text file when we close the window
    """
    def on_closing(self):
        if self.username != "" and self.password != "":
            try:
                f = open("userinfo.txt", "w")
                f.write(self.username + ":" + self.password)
                f.close()
            except IOError:
                pass
        self.socket_manager.close()
        self.Window.destroy()


GUI()
