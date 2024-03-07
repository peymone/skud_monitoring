from sys import argv

from model import model


class Console:
    """Class for user input and commands execution"""

    def __init__(self) -> None:
        self.__command = None
        self.__commands = {
            'commands': "Show all available commands",
            'exit': "Close console",
            'stop': "Stop client",
            'status': "Show current services status - for test",
        }

    def show_commands(self) -> None:
        """Show all available commands"""

        print('\n')

        for command, description in self.__commands.items():
            print(f"{command.ljust(45)}{description}")

        print('\n')

    def commands_handler(self) -> None:
        """Enter and execute command"""

        while self.__command != 'exit':
            try:  # Catch ctrl + c

                self.__command = input("Enter command /> ")

                match self.__command:  # Execute commands

                    case 'commands': self.show_commands()

                    case 'stop': model.stop_client()

                    case 'status':
                        services_statuses = model.get_servicesStatuses()
                        print('\n')

                        for status in services_statuses:
                            for service_name, status in status.items():
                                print(service_name.ljust(45), status[0].ljust(
                                    40), f'last log was {status[1]}')

                            print('\n')

                        print('\n')

            except KeyboardInterrupt:  # Ctrl + C
                self.__command = 'exit'

        print('\n')


if __name__ == '__main__':
    client_console = Console()

    if len(argv) > 1:  # Custom or standard server ip and port
        server_host, server_port = argv[1], int(argv[2])
    else:
        server_host, server_port = '10.40.21.3', 9186

    model.start_client(server_host, server_port)
    print("\nAvailable commands:")
    client_console.show_commands()
    client_console.commands_handler()
