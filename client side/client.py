from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from json import dumps
from time import sleep
import socket

from servicesChecker import services_checker


class Client:
    def __init__(self) -> None:
        self.__client_hostName = socket.gethostname()
        self.__server_hostName = None
        self.__server_portNumber = None
        self.__client_status = False

    def start(self, server_hostName: str, server_portNumber: int) -> None:
        self.__server_hostName = server_hostName
        self.__server_portNumber = server_portNumber
        self.__client_status = True

        while self.__client_status is True:
            try:  # Try to connect the server until it response
                self.client_socket: socket.socket = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect(
                    (self.__server_hostName, self.__server_portNumber))

                #  Send first message to the server - client host name
                self.client_socket.send(self.__client_hostName.encode('utf-8'))
                self.__client_status = True

                print(
                    f"\nClient is running, connected to {server_hostName}:{server_portNumber}\n")

                self.__recieve_messages_fromServer()

            # Rise this if the server is not working at the moment. Try againg after 60 seconds
            except ConnectionRefusedError:
                print(
                    f"\nServer on {server_hostName}:{server_portNumber} is not working at the moment. Client will try reconnect after 60 seconds\n")
                sleep(60)

            # No server on server_hostName:server_portNumber
            except TimeoutError:
                print(
                    f"\nServer on {server_hostName}:{server_portNumber} does not exist in this network. Client will try reconnect after 60 seconds\n")
                sleep(60)

    def stop(self) -> None:
        """Close connection by client"""

        if self.__client_status is False:
            print("\nClient is not working at the moment\n")
        else:
            self.client_socket.close()
            self.__client_status = False
            print(
                f"\nConnection to {self.__server_hostName}:{self.__server_portNumber} is closed by client\n")

    def __send(self, message: str) -> None:
        """Send messages to the server"""

        if self.__client_status is False:
            print("\nClient is not working at the moment\n")
        else:
            try:
                self.client_socket.send(message.encode('utf-8'))
            except BrokenPipeError:
                print(
                    f"\nServer on {self.__server_hostName}:{self.__server_portNumber} is not working at the moment\n")

    def __recieve_messages_fromServer(self) -> None:
        try:

            while self.__client_status is True:
                message: str = self.client_socket.recv(1024).decode('utf-8')
                if message == 'services_statuses':
                    services_statuses = model.get_servicesStatuses()
                    self.__send(dumps(services_statuses))

        # Connection closed by server
        except ConnectionResetError:
            self.client_socket.close()
            self.__client_status = False
            print(
                f"\nConnection to {self.__server_hostName}:{self.__server_portNumber} is closed by server\n")

        # Connection closed by client
        except ConnectionAbortedError:
            pass


class Model:
    """Class for getting data from checkers and return values"""

    def __init__(self) -> None:
        self.__client = Client()

    def get_servicesStatuses(self) -> tuple[dict[str, tuple[str]], dict[str, tuple[str]] | str]:
        """Get data services statuses from Lyrix and ostel checkers"""

        # Thread pool for parallel checkers execution
        with ThreadPoolExecutor(2) as pool:
            lyrixChecker_thread = pool.submit(
                services_checker.get_lyrixServices_status)
            ostelChecker_thread = pool.submit(
                services_checker.get_ostelServices_status)

            # Get results from threads
            lyrixServices_status = lyrixChecker_thread.result()
            ostelServices_status = ostelChecker_thread.result()

        return lyrixServices_status, ostelServices_status

    def start_client(self, server_hostName: str, server_portNumber: int) -> None:
        client_thread = Thread(target=self.__client.start, args=(
            server_hostName, server_portNumber), daemon=True)
        client_thread.start()

    def stop_client(self) -> None:
        self.__client.stop()


model = Model()
