from sys import argv

from model import model


class Console:
    def __init__(self) -> None:
        self.__command = None
        self.__commands = {
            'commands': "Show all available commands",
            'exit': "Close console",
            'start': "Start client",
            'stop': "Stop client",
            'status': "Show current services status - for test",
        }

    def show_commands(self) -> None:
        """Show all available commands"""
        print('\n')

        for command, description in self.__commands.items():
            print(f"{command.ljust(60)}{description}")

        print('\n')

    def commands_handler(self) -> None:
        while self.__command != 'exit':
            try:
                # Enter commands until 'exit'
                self.__command = input("Enter command /> ")

                # Execute command
                match self.__command:
                    case 'commands': self.show_commands()
                    case 'start': pass
                    case 'stop': pass
                    case 'status':
                        services_statuses = model.get_servicesStatuses()
                        print('\n')
                        for status in services_statuses:
                            for service_name, result in status.items():
                                print(service_name.ljust(50),
                                      result[0].ljust(40), f'last log was {result[1]}')
                            print('\n')

            except KeyboardInterrupt:
                self.__command = 'exit'

        print('\n')


if __name__ == '__main__':
    client_console = Console()
    print("\nAvailable commands:")
    client_console.show_commands()
    client_console.commands_handler()

    if len(argv) > 1:
        server_host, server_port = argv[1], int(argv[2])
    else:
        server_host, server_port = '10.40.21.3', 9186
