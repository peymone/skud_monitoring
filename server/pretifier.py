from time import sleep, localtime, strftime

from rich.console import Console
from rich.theme import Theme
from rich.progress import track


class Pretifier:
    """Class for console styling"""

    def __init__(self) -> None:
        self.__custom_theme = Theme({
            'system': 'dim cyan',
            'commands': 'cyan',
            'debug': 'white',
            'info': 'green',
            'warning': 'yellow1',
            'error': 'bold red1 blink',
            'critical': 'bold orange_red1 blink'
        })

        self.__custom_console = Console(theme=self.__custom_theme)
        self.progressBar_status = None

    def progress_bar(self, delay: int) -> None:
        """Show progress bar with specific delay"""

        self.progressBar_status = True
        print('\n')

        for n in track(range(100), description="Getting data..."):
            if self.progressBar_status is True:
                sleep(delay/100)
            else:
                break

    def show(self, message: str, lvl: str = 'debug') -> None:
        """Print message with custom styling"""

        time_now = strftime("%d.%m %A %H:%M", localtime())
        self.__custom_console.print(f"{time_now}\t{message}", style=lvl)

    def enter(self, prompt: str, lvl: str = 'debug') -> str:
        """Input user command with custom styling"""

        return self.__custom_console.input(f"[{lvl}]{prompt}")


rich = Pretifier()
