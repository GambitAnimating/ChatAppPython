import json
import socket
import threading
import psycopg2.extras
import psycopg2.errors
import uuid
import bcrypt
import re


class SQLManager:
    conn = psycopg2.connect(database="root_db", user="root", password="", host="localhost", port="5432")

    def try_login(self, username, password):
        cur = self.conn.cursor()

        username = username.lower()

        cur.execute("SELECT user_uid, username, email, password from user_account WHERE username='%s'" % username)
        row = cur.fetchone()
        error = ""
        if row is not None:
            if bcrypt.checkpw(bytes(password, 'utf-8'), bytes(row[3])):
                print("Logged in", row[1])
                return True, ""
            else:
                error = "Incorrect Password"
        else:
            error = "User does not exist"
        return False, error

    def try_register(self, username, email, password):
        cur = self.conn.cursor()

        username = username.lower()
        email = email.lower()

        if not re.search("^[A-Za-z0-9]+(?:[ _-][A-Za-z0-9]+)*$", username):
            return False, "Invalid username"

        if not re.search(
                "^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$",
                email):
            return False, "Invalid email"

        if not re.search("^(?=.{6,20}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9.!_]+(?<![_.])$", password):
            return False, "Invalid password"

        hashed_pw = bcrypt.hashpw(bytes(password, 'utf-8'), bcrypt.gensalt())

        psycopg2.extras.register_uuid()
        user_uid = str(uuid.uuid4())

        error = ""

        try:
            cur.execute("INSERT INTO user_account (user_uid,username,email,password) VALUES(%s,%s,%s,%s)",
                        (user_uid, username, email, hashed_pw.decode()))
            return True, ""
        except psycopg2.errors.UniqueViolation as e:

            error = e.diag
            detail = error.message_detail
            error = detail.split("(")[1].split(")")[0].capitalize() + detail.split("(")[2].split(")")[1]
        finally:
            self.conn.commit()

        return False, error


FORMAT = "utf-8"

clients = []
names = {}

messages = "lol"

server = socket.socket()
print("Socket successfully created!")

port = 8080

server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('', port))

server.listen()
print("Socket listening")


class SocketManager():
    def __init__(self):
        self.messages = str()
        self.sql_manager = SQLManager()
        self.start()

        messages = ""

    def start(self):
        sql_manager = SQLManager()
        try:
            while True:
                # accept connections and returns
                # a new connection to the client
                #  and  the address bound to it
                conn, addr = server.accept()

                # append the name and client
                # to the respective list
                clients.append(conn)

                conn.sendall('Connection successful!'.encode(FORMAT))

                # Start the handling thread
                thread = threading.Thread(target=self.handle,
                                          args=(conn, addr))
                thread.start()

                # no. of clients connected
                # to the server
                print(f"active connections {threading.active_count() - 1}")
        except KeyboardInterrupt:
            print("Application closed, close socket")
            server.close()

    def handle(self, conn, addr):
        print(f"new connection {addr}")
        connected = True

        while connected:
            try:
                response_data = self.recvjson(conn, self)
                if response_data is None:
                    break

                packet_type = response_data['type']

                if packet_type == "REGISTER":
                    username = response_data['username']
                    email = response_data['email']
                    password = response_data['password']
                    success, error = self.sql_manager.try_register(username, email, password)
                    response_json = {"type": "REGISTER", "success": success, "error": error}
                    if (success):
                        names[conn] = username
                    self.sendjson(conn, response_json)

                if packet_type == "LOGIN":
                    username = response_data['username']
                    password = response_data['password']
                    success, error = self.sql_manager.try_login(username, password)
                    response_json = {"type": "LOGIN", "success": success, "error": error}
                    if (success):
                        names[conn] = username
                    self.sendjson(conn, response_json)

                if packet_type == "JOINED_SERVER":
                    self.messages += str(names[conn]) + " has joined!" + '\n\n'
                    response_json = {"type": "OLD_MESSAGES", "messages": self.messages}
                    if self.messages != "":
                        self.sendjson(conn, response_json)

                if packet_type == "CHAT_MESSAGE":
                    message = response_data['message']
                    self.broadcast_message(conn, message)


            except ConnectionResetError:
                print("Connection was reset by the client")
                clients.remove(conn)
                connected = False

    def broadcast_message(self, sender=None, message=None):
        if sender is not None and sender in names:
            message = names[sender] + ": " + message

        message += '\n\n';

        self.messages += message

        response_json = {"type": "CHAT_MESSAGE", "message": message}

        for client in clients:
            self.sendjson(client, response_json)

    @staticmethod
    def sendjson(conn, data):
        response_json = json.dumps(data)
        header = len(response_json).to_bytes(4, 'big')
        conn.sendall(header + response_json.encode())
        # try:
        #
        # except BrokenPipeError as e:
        #     print("Error: Broken pipe. Closing socket.")
        #     clients.remove(conn)
        #     conn.close()
        # except OSError:
        #     clients.remove(conn)
        #     conn.close()

    @staticmethod
    def recvjson(conn, caller):
        header = conn.recv(4)
        # If the header is empty, the connection has been closed
        if not header:
            caller.broadcast_message(message=(names[conn] + " has left."))
            print("The connection has been closed")
            clients.remove(conn)
            return None

        json_length = int.from_bytes(header, 'big')

        message = b''
        while len(message) < json_length:
            chunk = conn.recv(json_length - len(message))
            if chunk == b'':
                raise RuntimeError("Socket connection broken")
                clients.remove(conn)
            message += chunk
        response_data = json.loads(message.decode())
        return response_data


SocketManager()
