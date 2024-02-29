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
        while True:
            try:
                self.client_socket = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect(
                    (self.__server_hostName, self.__server_portNumber))

                self.client_socket.send(self.__client_hostName.encode('utf-8'))
                self.__client_status = True

            except ConnectionRefusedError:
                sleep(60)

    def recieve_messages_fromServer(self):
        try:
            while self.__client_status is True:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message == 'services_statuses':
                    model.get_servicesStatuses()

        except ConnectionResetError:
            self.client_socket.close()
            self.__client_status = False

        except ConnectionAbortedError:
            pass


client = Client()
