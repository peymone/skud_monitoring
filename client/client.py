from json import dumps
from time import sleep
import socket

from model import model


class Client:
    def __init__(self) -> None:
        self.__client_hostName = socket.gethostname()
        self.__server_hostName = None
        self.__server_portNumber = None
        self.__client_status = False

    def start(self, server_hostName, server_portNumber):
        self.__server_hostName = server_hostName
        self.__server_portNumber = server_portNumber

        while True:
            try:  # Try to connect the server until it response
                self.client_socket = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect(
                    (self.__server_hostName, self.__server_portNumber))

                # Send first message to the server - client host name
                self.client_socket.send(self.__client_hostName.encode('utf-8'))
                self.__client_status = True

                print(
                    f"\nClient is running, connected to {server_hostName}:{server_portNumber}\n")
                self.__recieve_messages_fromServer()

            # Rise this if the server is not working at the moment. Try againg after 60 seconds
            except ConnectionRefusedError:
                sleep(60)

    def __recieve_messages_fromServer(self):
        try:
            while self.__client_status is True:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message == 'services_statuses':
                    status = model.get_servicesStatuses()

        # Connection closed by server
        except ConnectionResetError:
            self.client_socket.close()
            self.__client_status = False
            print(
                f"\nConnection to {self.__server_hostName}:{self.__server_portNumber} is closed\n")

        # Connection closed by client
        except ConnectionAbortedError:
            pass


client = Client()
