import json
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import Tk

from login import LoginGUI
from register import RegisterGUI
from chat_form import ChatGUI
import socket


class SocketManager:
    client = socket.socket()

    port = 8080
    FORMAT = "utf-8"

    connected = False

    def connect(self, gui):
        self.client.connect(('74.208.5.206', self.port))
        conf_msg = self.client.recv(1024).decode()
        print(conf_msg)
        self.connected = True
        self.gui = gui

    def try_login(self, username, password):
        response_json = {"type": "LOGIN", "username": username, "password": password}
        self.sendjson(self.client, response_json)

        try:
            response_data = self.recvjson(self.client)
            if response_data is None:
                return False, 'Connection Error'
            packet_type = response_data['type']

            if packet_type == 'LOGIN':
                return response_data['success'], response_data['error']
        except ConnectionResetError:
            print('ConnectionResetError')
            return False, 'Connection refused'

        return False, 'Unknown Error'

    def try_register(self, username, email, password):
        response_json = {"type": "REGISTER", "username": username, "email": email, "password": password}
        self.sendjson(self.client, response_json)

        try:
            response_data = self.recvjson(self.client)
            if response_data is None:
                return False, 'Connection Error'
            packet_type = response_data['type']
            if packet_type == 'REGISTER':
                return response_data['success'], response_data['error']

        except ConnectionResetError:
            print('ConnectionResetError')
            return False, 'Connection refused'

        return False, 'Unknown Error'

    def start_chat(self):
        # the thread to receive messages
        rcv = threading.Thread(target=self.receive)
        rcv.start()

        response_json = {"type": "JOINED_SERVER"}
        self.sendjson(self.client, response_json)


    def send_chat(self, message):
        response_json = {"type": "CHAT_MESSAGE", "message": message}
        self.sendjson(self.client, response_json)

    def receive(self):
        while self.connected:
            try:
                response_data = self.recvjson(self.client)
                if response_data is None:
                    self.connected = False
                    break
                packet_type = response_data['type']

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

    def close(self):
        self.connected = False
        self.client.close()

    @staticmethod
    def sendjson(conn, data):
        response_json = json.dumps(data)
        header = len(response_json).to_bytes(4, 'big')
        conn.sendall(header + response_json.encode())

    @staticmethod
    def recvjson(conn):
        try:
            header = conn.recv(4)
            # If the header is empty, the connection has been closed
            if not header:
                print("The connection has been closed")
                return None

            json_length = int.from_bytes(header, 'big')
            print(json_length)
            message = b''
            while len(message) < json_length:

                chunk = conn.recv(json_length - len(message))
                print(chunk)
                if chunk == b'':
                    raise RuntimeError("Socket connection broken")
                message += chunk
            response_data = json.loads(message.decode())
            return response_data
        except OSError:
            print("OS Error")


# class SQLManager:
#     conn = psycopg2.connect(database="registration_test", user="jedgould", password="", host="localhost", port="5432")
#
#     def try_login(self, username, password):
#         cur = self.conn.cursor()
#
#         username = username.lower()
#
#         cur.execute("SELECT user_uid, username, email, password from user_account WHERE username='%s'" % username)
#         row = cur.fetchone()
#         if row is not None:
#             if bcrypt.checkpw(bytes(password, 'utf-8'), bytes(row[3])):
#                 print("Logged in", row[1])
#                 return True, ""
#             else:
#                 error = "Incorrect Password"
#         else:
#             error = "User does not exist"
#         return False, error
#
#     def try_register(self, username, email, password):
#         cur = self.conn.cursor()
#
#         username = username.lower()
#         email = email.lower()
#
#         if not re.search("^[A-Za-z0-9]+(?:[ _-][A-Za-z0-9]+)*$", username):
#             return False, "Invalid username"
#
#         if not re.search(
#                 "^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$",
#                 email):
#             return False, "Invalid email"
#
#         if not re.search("^(?=.{6,20}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9.!_]+(?<![_.])$", password):
#             return False, "Invalid password"
#
#         hashed_pw = bcrypt.hashpw(bytes(password, 'utf-8'), bcrypt.gensalt())
#
#         psycopg2.extras.register_uuid()
#         user_uid = str(uuid.uuid4())
#
#         error = ""
#
#         try:
#             cur.execute("INSERT INTO user_account (user_uid,username,email,password) VALUES(%s,%s,%s,%s)",
#                         (user_uid, username, email, hashed_pw.decode()))
#             return True, ""
#         except psycopg2.errors.UniqueViolation as e:
#
#             error = e.diag
#             detail = error.message_detail
#             error = detail.split("(")[1].split(")")[0].capitalize() + detail.split("(")[2].split(")")[1]
#         finally:
#             self.conn.commit()
#
#         return False, error


class GUI:
    username = ""
    password = ""
    # constructor method
    def __init__(self):
        self.socket_manager = SocketManager()
        self.socket_manager.connect(self)

        self.login_GUI, self.register_GUI, self.chat_GUI = None, None, None

        self.Window = Tk()
        self.Window.tk.call("source", "azure.tcl")
        self.Window.tk.call("set_theme", "dark")
        self.Window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.login_GUI = LoginGUI(self)

        self.Window.mainloop()

    def goto_register(self):
        self.register_GUI = RegisterGUI(self)

    def show_chat(self):
        self.chat_GUI = ChatGUI(self)

    def goto_login(self):
        self.login_GUI = LoginGUI(self)

    def set_login_info(self, username, password):
        self.username = username
        self.password = password

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
