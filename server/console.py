from threading import Thread
from sys import argv

# Import application modules
from server import monitor
from pretifier import rich
from logger import logger


class Console:
    """Class for user input"""

    def __init__(self) -> None:
        self.__command = None
        self.__commands = {
            'exit': "Close the admin_console",
            'commands': "Show all available commands",

            'monitor_start |minutes|': "Start system monitoring every n minutes (15 by default)",
            'monitor_stop': "Stop system monitoring",
            'monitor_status': "Show current monitor status",
            'monitor_delay': "Show system monitoring delay",
            'monitor_delay |minutes|': "Change system monitoring delay to (minutes)",

            'server_start': "Start server",
            'server_stop': "Stop server",
            'server_status': "Show current server status",
            'server_clients': 'Show current connected clients',
        }

    def show_commands(self) -> None:
        """Show all available commands"""

        print('\n')

        for command, description in self.__commands.items():
            rich.show(f"{command.ljust(45)}{description}", lvl='commands')

        print('\n')

    def commands_handler(self) -> None:
        """Enter and execute command"""

        while self.__command != 'exit':
            try:  # Catch ctrl + c

                self.__command = rich.enter("Enter command /> ", 'system')
                rich.progressBar_status = False

                # Check if command have more than 1 word
                if len(self.__command.split()) >= 2:
                    command_msg = self.__command.split()[0]
                    command_arg = self.__command.split()[1]
                else:
                    command_msg = self.__command
                    command_arg = None

                match command_msg:  # Execute commands
                    case 'commands': self.show_commands()

                    case 'monitor_start':
                        if command_arg is not None:
                            try:  # Check if command arg is integer
                                delay = int(command_arg)
                                monitor_thread = Thread(
                                    target=monitor.start, daemon=True, args=(delay,))
                                monitor_thread.start()

                            except ValueError:
                                print('\n')
                                rich.show(
                                    "Monitor delay has to be integer", lvl='warning')
                                print('\n')

                        else:  # Command argument is empty
                            monitor_thread = Thread(
                                target=monitor.start, daemon=True)
                            monitor_thread.start()

                    case 'monitor_stop': monitor.stop()

                    case 'monitor_status': monitor.status()

                    case 'monitor_delay':
                        if command_arg is not None:
                            try:  # Check if command arg is integer
                                delay = int(command_arg)
                                monitor.change_delay(delay)

                            except ValueError:
                                print('\n')
                                rich.show(
                                    "Monitor delay has to be integer", lvl='warning')
                                print('\n')

                        else:  # Command argument is empty
                            monitor.show_delay()

                    case 'server_start': monitor.start_server()

                    case 'server_stop': monitor.stop_server()

                    case 'server_status': monitor.server_status()

                    case 'server_clients': monitor.server_clients()

            except KeyboardInterrupt:  # Ctrl + C
                self.__command = 'exit'

        logger.log.debug("Progamm was closed")
        print('\n')


if __name__ == '__main__':
    admin_console = Console()
    logger.log.debug("Proram was started")

    if len(argv) > 1:  # Custom or standard port
        server_portNumber = int(argv[1])
    else:
        server_portNumber = 9186

    print('\n')
    rich.show("Available commands:", lvl='system')
    admin_console.show_commands()
    admin_console.commands_handler()
