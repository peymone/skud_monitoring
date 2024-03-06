from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from json import dumps
from time import sleep
import socket

from servicesChecker import services_checker


class Client:
    """Class for creating client socket and communicate with server"""

    def __init__(self) -> None:
        self.status = False
        self.__hostName = socket.gethostname()

    def start(self, server_hostName: str, server_portNumber: int) -> None:
        """Create client socket and connect to the server"""

        self.__server_hostName = server_hostName
        self.__server_portNumber = server_portNumber
        self.status = True

        # Try to connect the server if client is working
        while self.status is True:
            try:  # Try to connect the server until it response

                # Create client socket
                self.__clientSocket: socket.socket = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)

                # Connect to the server
                self.__clientSocket.connect(
                    (self.__server_hostName, self.__server_portNumber))

                #  Send first message to the server - client host name
                self.__clientSocket.send(self.__hostName.encode('utf-8'))

                print(
                    f"\nClient is running, connected to {server_hostName}:{server_portNumber}\n")

                self.__receive_messages()

            except ConnectionRefusedError:  # Server is not working at the moment
                print(
                    f"\nServer on {server_hostName}:{server_portNumber} is not working at the moment. Client will try reconnect after 60 seconds\n")

                sleep(60)

            except TimeoutError:  # There is no server on the specified ip and port
                print(
                    f"\nServer on {server_hostName}:{server_portNumber} does not exist in this network. Client will try reconnect after 60 seconds\n")

                sleep(60)

    def stop(self) -> None:
        """Break connection with server by closing client socket"""

        if self.status is False:
            print("\nClient is not working at the moment\n")
        else:
            self.__clientSocket.close()
            self.status = False
            print(
                f"\nConnection to {self.__server_hostName}:{self.__server_portNumber} is closed by client\n")

    def __send(self, message: str) -> None:
        """Send message to the server"""

        if self.status is False:
            print("\nClient is not working at the moment\n")
        else:
            try:
                self.__clientSocket.send(message.encode('utf-8'))
            except BrokenPipeError:
                print(
                    f"\nServer on {self.__server_hostName}:{self.__server_portNumber} is not working at the moment\n")

    def __receive_messages(self) -> None:
        """Receiving messages from server"""

        try:
            while self.status is True:
                message: str = self.__clientSocket.recv(1024).decode('utf-8')

                match message:
                    case 'services_statuses':
                        services_statuses = model.get_servicesStatuses()
                        self.__send('services_statuses')
                        self.__send(dumps(services_statuses))

                    case _: pass

        except ConnectionResetError:  # Connection closed by server
            self.__clientSocket.close()
            self.status = False
            print(
                f"\nConnection to {self.__server_hostName}:{self.__server_portNumber} is closed by server\n")

        except ConnectionAbortedError:  # Connection closed by client
            pass


class Model:
    """Class for getting data from checkers and return values"""

    def __init__(self) -> None:
        self.__client = Client()

    def get_servicesStatuses(self) -> tuple[dict[str, tuple[str]], dict[str, tuple[str]] | str]:
        """Get services statuses from Lyrix and ostel checkers"""

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
        """Start client with specific server host name and port number"""

        if self.__client.start is False:
            client_thread = Thread(target=self.__client.start, args=(
                server_hostName, server_portNumber), daemon=True)

            client_thread.start()
        else:
            print("\nClient is already working\n")

    def stop_client(self) -> None:
        """Stop client, break connection to the server"""

        self.__client.stop()


model = Model()
