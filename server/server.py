from concurrent.futures import ThreadPoolExecutor
from threading import Thread, Event
from json import load
import socket

# Import application modules
from servers_check.checker import servers_checker
from api_check.checker import api_checker
from pretifier import rich, sleep
from logger import logger


class Server:
    """Create socket and start communicate with clients"""

    def __init__(self) -> None:
        self.status = False
        self.__host = socket.gethostbyname(socket.gethostname())
        self.__port = None
        self.__clients: dict[str, list] = dict()

    def start(self, port: int) -> None:
        """Start server"""

        try:  # Create socket and start receiving messages from clients
            self.__port = port
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.bind((self.__host, self.__port))
            self.__socket.listen()  # Set socket to listen mod
            self.status = True

            print('\n')
            rich.show(
                f"Server is running on {self.__host}:{self.__port}. Waiting for connections")
            logger.log.debug(
                f"Server is running on {self.__host}:{self.__port}. Waiting for connections")
            print('\n')

            # Accept clients and start receiving messages
            while self.status is True:
                client_socket, client_address = self.__socket.accept()
                client_thread = Thread(target=self.__receive_messages, args=(
                    client_socket, client_address), daemon=True)
                client_thread.start()

        except OSError:
            pass

    def stop(self) -> None:
        """Close server socket and break connections"""

        print('\n')

        if self.status is False:
            rich.show("Server is not working at the moment", lvl='warning')
        else:
            self.__clients = dict()
            self.__socket.close()
            self.status = False

            rich.show("Server has been stopped")
            logger.log.debug("Server has been stopped by admin")

        print('\n')

    def show_status(self) -> None:
        """Show current server status"""

        print('\n')

        if self.status is False:
            rich.show("Server is not working")
        else:
            rich.show("Server is working")

        print('\n')

    def show_clients(self) -> None:
        """Show current connected clients to the server"""

        print('\n')

        if self.status is False:
            rich.show("Server is not working at the moment", lvl='warning')
        elif len(self.__clients) == 0:
            rich.show("Server have no connected clients at the moments")
        else:  # Show client host name and address
            for client_hostName, client_data in self.__clients.items():
                rich.show(f"{client_hostName.ljust(45)}{client_data[1]}")

        print('\n')

    def __receive_messages(self, client_socket, client_address) -> None:
        """Receiving messages from specific client"""

        # Type hints for services statuses
        services_statuses = tuple[dict[str, tuple[str]],
                                  dict[str, tuple[str] | str]]

        try:  # Receiving messages from client

            # Receive first message from client and fill clients dict
            client_hostName: str = client_socket.recv(1024).decode('utf-8')
            self.__clients[client_hostName] = [
                client_socket, client_address, None]

            logger.log.debug(
                f"{client_address} established connection with name {client_hostName}")

            # Receiving messages from client until client socket closed
            while client_hostName in self.__clients.keys():
                message: str = client_socket.recv(1024).decode('utf-8')

                match message:  # Handle commands from client
                    case 'services_statuses':
                        # Receive services statuses and add to clients dictionary
                        services_statuses = load(
                            client_socket.recv(1024).decode('utf-8'))

                        self.__clients[client_hostName][-1] = services_statuses

                    case _: pass  # Add command if needed

        except ConnectionResetError:  # Connection closed by client
            logger.log.debug(
                f"{client_address} with name {client_hostName} disconnected")

            del self.__clients[client_hostName]

        except ConnectionAbortedError:  # Connection closed by server
            pass

    def get_servicesStatuses(self) -> None:
        """Send command to all connected clients for get services statuses"""

        # Pass if server is not working or have no connected clients
        if self.status is False or len(self.__clients) == 0:
            pass
        else:  # Iterate over all connected clients, send command
            for client_hostName, client_data in self.__clients.items():
                client_data[0].send('services_statuses'.encode('utf-8'))

        sleep(10)  # Need time for receiving statuses from clients
        servicesStatuses_received = all(
            [statuses[-1] for statuses in self.__clients.values()])

        # Check if all services statuses is received
        while servicesStatuses_received is not True:
            sleep(5)  # Need more time for receiving statuses
            servicesStatuses_received = all(
                [statuses[-1] for statuses in self.__clients.values()])

        self.__show_servicesStatuses()  # Show services statuses if all received

    def __show_servicesStatuses(self) -> None:
        """Show services statuses if all received"""

        # Iterate over all connected clients, print statuses
        for client_hostName, client_data in self.__clients.items():

            lyrixServices_statusMsg = [status[-1][0] for status in client_data]
            ostelServices_statusMsg = [status[-1][1] for status in client_data]

            # Print Lyrix services statuses
            if 'Down' in lyrixServices_statusMsg or 'pid not found' in lyrixServices_statusMsg:
                rich.show(
                    f"Lyrix services on {client_hostName} have some problems:", lvl='warning')
                logger.log.warning(
                    f"Lyrix services on {client_hostName} have some problems:")
                print('\n')

                for service_name, status in client_data[-1][0].items():
                    if status[0] == 'Down':
                        rich.show(
                            f"{service_name.ljust(45)}{status[0].ljust(40)}last log was {status[1]}", lvl='error')
                        logger.log.error(
                            f"{service_name.ljust(45)}{status[0].ljust(40)}last log was {status[1]}")

                    elif status[0] == 'pid not found':
                        rich.show(
                            f"{service_name.ljust(45)}{status[0].ljust(40)}last log was {status[1]}", lvl='warning')
                        logger.log.warning(
                            f"{service_name.ljust(45)}{status[0].ljust(40)}last log was {status[1]}")

            else:  # All Lyrix services is Up
                rich.show(
                    f"All Lyrix services on {client_hostName} is Up", lvl='info')
                logger.log.info(
                    f"All Lyrix services on {client_hostName} is Up")

            print('\n')

            # Print Ostel services statuses
            if 'Down' in ostelServices_statusMsg or 'Warning' in ostelServices_statusMsg:
                rich.show(
                    f"Ostel services on {client_hostName} have some problems:", lvl='critical')
                logger.log.critical(
                    f"Ostel services on {client_hostName} have some problems:")
                print('\n')

                for service_name, status in client_data[-1][1].items():
                    if status[0] == 'Down':
                        rich.show(
                            f"{service_name.ljust(45)}{status[0].ljust(40)}last log was {status[1]}", lvl='critical')
                        logger.log.critical(
                            f"{service_name.ljust(45)}{status[0].ljust(40)}last log was {status[1]}")

                    elif status[0] == 'Warning':
                        rich.show(
                            f"{service_name.ljust(45)}{status[0].ljust(40)}last log was {status[1]}", lvl='warning')
                        logger.log.warning(
                            f"{service_name.ljust(45)}{status[0].ljust(40)}last log was {status[1]}")

            else:  # All Ostel services is Up
                rich.show(
                    f"All Ostel services on {client_hostName} is Up", lvl='info')
                logger.log.info(
                    f"All Ostel services on {client_hostName} is Up")

            print('\n')

            # Reset recived services statuses flag
            self.__clients[client_hostName][-1] = None


class Monitor:
    """Get and show data from checkers"""

    def __init__(self) -> None:
        self.__isActive = None
        self.__delay = None
        self.__event = Event()
        self.__server = Server()

    def start(self, delay: int = 15) -> None:
        """Get dada from checkers every n minutes"""

        if self.__isActive:  # Check if monitor is already working
            print('\n')
            rich.show("Monitor is already working", lvl='warning')
            print('\n')

        else:  # Start system monitoring
            self.__delay = delay * 60  # Convert minutes to seconds
            self.__isActive = True

            print('\n')
            rich.show(
                f"System monitoring has been started with {delay} minutes delay")
            logger.log.debug(
                f"System monitoring has been started with {delay} minutes delay")

            while self.__isActive:  # Start monitoring loop

                # Create a threads pool for get checkers data and parallel execution
                with ThreadPoolExecutor(2) as pull:

                    # Start threads
                    servers_status_thread = pull.submit(servers_checker.ping)
                    api_status_thread = pull.submit(api_checker.http_request)

                    # Create logs for starting threads
                    logger.log.debug("Checker threads has been started")

                    # getting results from threads
                    servers_status = servers_status_thread.result()
                    api_status = api_status_thread.result()

                    # Create log for ending threads
                    logger.log.debug("Checker threads has been ended")

                print('\n')
                rich.show("Servers status:\n")

                # Print current servers statuses
                for server, status in servers_status.items():

                    if status[0] == 'down':  # Check if one of the servers is down
                        rich.show(
                            f"{server.ljust(45)}{status[0].ljust(40)}{status[1]}", lvl='error')
                        logger.log.error(f"{server} is down - ping check")

                    elif 'up (package loss' in status[0]:  # Loss 1 - 99%
                        rich.show(
                            f"{server.ljust(45)}{status[0].ljust(40)}{status[1]}", lvl='warning')
                        logger.log.warning(
                            f"{server} is {status[0]} - ping check")

                    else:
                        rich.show(
                            f"{server.ljust(45)}{status[0].ljust(40)}{status[1]}", lvl='info')
                        logger.log.info(f"{server} is up - ping check")

                print('\n')
                rich.show("API's status:\n")

                # Print current API's statuses
                for api, status in api_status.items():

                    if status[0] == 'down':  # Check if one of API's is down
                        rich.show(
                            f"{api.ljust(45)}{status[0].ljust(40)}{status[1]}", lvl='critical')
                        logger.log.critical(
                            f"{api} is down - http status check ({status[1]})")

                    else:
                        rich.show(
                            f"{api.ljust(45)}{status[0].ljust(40)}{status[1]}", lvl='info')
                        logger.log.info(
                            f"{api} is up - http status check ({status[1]})")

                # Print current services statuses from SKUD servers
                self.__server.get_servicesStatuses()

                # Show progress bar and wait for delay passing
                progressBar_thread = Thread(
                    target=rich.progress_bar, args=(self.__delay,), daemon=True)

                logger.log.debug("Progress bar thread has been started")
                progressBar_thread.start()  # Start progress bar thread
                logger.log.debug("Progress bar thread has been ended")

                # Wait for delay pass or event - loop can stop immediately
                self.__event.wait(self.__delay)

                progressBar_thread.join()  # Wait until progress bar end
                self.__event.clear()  # Set the event to False

    def stop(self) -> None:
        """Stop system monitoring"""

        print('\n')

        if self.__isActive is True:
            self.__isActive = False
            self.__event.set()  # Set event to True - start loop can stop immediately
            rich.show("System monitoring has been stopped")
            logger.log.debug("System monitoring has been stopped by admin")
        else:
            rich.show("Monitor is not working at the moment", lvl='warning')

        print('\n')

    def status(self) -> None:
        """Show system monitoring status"""

        print('\n')

        if self.__isActive:
            rich.show("Monitor is working")
        else:
            rich.show("Monitor is not working")

        print('\n')

    def show_delay(self) -> None:
        """Show system monitoring delay"""

        print('\n')

        if self.__isActive:
            rich.show(f"Monitor delay is {self.__delay//60} minutes")
        else:
            rich.show("Monitor is not working at the moment", lvl='warning')

        print('\n')

    def change_delay(self, delay: int) -> None:
        """Change delay for system monitoring"""

        print('\n')

        if self.__isActive:
            self.__delay = delay * 60  # Conver minutes to seconds
            self.__event.set()  # Set event to True - start loop can stop immediately

            rich.show(f"Monitor delay has been changed to {delay} minutes")
            logger.log.debug(
                f"Monitor delay has been changed to {delay} minutes")
        else:
            rich.show("Monitor is not working at the moment", lvl='warning')

        print('\n')

    def start_server(self, port: int) -> None:
        """Start server on specific port or 9186"""

        if self.__server.status is False:
            server_thread = Thread(
                target=self.__server.start, args=(port,), daemon=True)
            server_thread.start()
        else:
            print('\n')
            rich.show("Server is already working", lvl='warning')
            print('\n')

    def stop_server(self) -> None:
        """Stop server"""

        self.__server.stop()

    def server_status(self) -> None:
        """Show current server status"""

        self.__server.show_status()

    def server_clients(self) -> None:
        """Show current connected clients to the server"""

        self.__server.show_clients()


monitor = Monitor()
