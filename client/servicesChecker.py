from pathlib import Path
from os.path import getmtime as modification_date
from datetime import datetime, timedelta
from os import popen
import re


class ServicesChecker:
    """Check service statuses, both lyrix and ostel"""

    def __init__(self) -> None:
        self.__LyrixLogs_path = Path(
            r'C:\Users\from_\Downloads\test_logs\LyrixLogs')
        self.__OstelLogs_path = Path(
            r'C:\Users\from_\Downloads\test_logs\OstelLogs')
        self.__lastLogTime_pattern = '\d{4}-[\d-]+\s[\d:]+'
        self.__pid_pattern = 'PID\s\d+'
        self.__logTime_format = '%Y-%m-%d %H:%M:%S'

        # List with Lyrix service names on specific server
        self.lyrix_services: list[str] = [re.search(r'\w+', log.stem).group()
                                          for log in self.__LyrixLogs_path.iterdir()]

        # Remove dublicates from secrvices list
        self.lyrix_services: set[str] = set(self.lyrix_services)

        # Remove unnecessary files from services list
        if 'kernelDiag' in self.lyrix_services:
            self.lyrix_services.remove('kernelDiag')
        if 'default' in self.lyrix_services:
            self.lyrix_services.remove('default')
        if 'console' in self.lyrix_services:
            self.lyrix_services.remove('console')

    def __get_lastLogTime(self, log_path: Path) -> datetime:
        """Get last log time from log"""

        # Opens log with 'cp866' encoding for Russian symbols support
        with open(log_path, mode='r', encoding='cp866') as log:
            for line in log:  # Check for last log time, rewrite until last occurrence
                log_timeMatch = re.match(self.__lastLogTime_pattern, line)
                if log_timeMatch is not None:
                    last_logTime = log_timeMatch.group()

            # Convert last log time string in file to datetime object
            last_logTime: datetime = datetime.strptime(
                last_logTime, self.__logTime_format)

            return last_logTime

    def __generate_currentLyrixLogs(self) -> dict[str, list[Path]]:
        """Generate current Lyrix service log paths in directory - they can change by time"""

        # Dict with service names and empty lists of log paths
        lyrix_logs = {service_name: [] for service_name in self.lyrix_services}

        # Fill list of log paths with paths currently presents in directory
        for service_name in self.lyrix_services:
            for log_path in self.__LyrixLogs_path.iterdir():
                if service_name in log_path.stem and log_path.stem != 'kernelDiag':
                    lyrix_logs[service_name].append(log_path)

        # Sort logs paths by modification date in reverse order
        for logs_pathsList in lyrix_logs.values():
            logs_pathsList.sort(key=modification_date, reverse=True)

        return lyrix_logs

    def get_lyrixServices_status(self) -> dict[str, tuple[str]]:
        """Get current lyrix service statuses by check process activity and last log time"""

        lyrixServices_status: dict[str, tuple] = dict()  # Result variable

        # Iterate over services in modification date order, check logs for PID pattern
        for service_name, logs_pathsList in self.__generate_currentLyrixLogs().items():
            pid = None

            for log_path in logs_pathsList:

                # Check last modificated log and get last log time
                if logs_pathsList.index(log_path) == 0:
                    last_logTime = self.__get_lastLogTime(log_path)
                    last_logTime = last_logTime.strftime(self.__logTime_format)

                # Open log and check for PID, example: PID 13813
                with open(log_path, mode='r') as log:
                    for line in log:  # Rewrite pid by last occurrence in log
                        pid_match = re.search(self.__pid_pattern, line)
                        if pid_match is not None:
                            pid: str = pid_match.group().split()[1]

                # Check if pid found and find process, move to next log otherwise. Write status result
                if pid is None:
                    lyrixServices_status[service_name] = 'pid not found', last_logTime
                else:
                    # Run cmd process check and support Russian language
                    process_check: str = popen(
                        f'tasklist /fi "pid eq {pid}"').read()
                    process_check: str = process_check.encode(
                        'cp1251').decode('cp866')

                    # Determinate status by cmd response
                    process_status = 'Up' if re.search(
                        '=+', process_check) else 'Down'

                    lyrixServices_status[service_name] = process_status, last_logTime
                    break

        return lyrixServices_status

    def get_ostelServices_status(self) -> dict[str, tuple[str]] | str:
        """Get current ostel service statuses by check last log time"""

        ostelServices_status: dict[str, tuple[str]] = dict()
        timedelta_30m = timedelta(minutes=30)
        timedelta_180m = timedelta(minutes=120)

        if self.__OstelLogs_path.exists():

            # Generate current ostel service log paths in directory - they can change by time
            ostel_logs = {
                log_path.stem: log_path for log_path in self.__OstelLogs_path.iterdir() if log_path.suffix == '.log'}

            for service_name, log_path in ostel_logs.items():
                last_logTime = self.__get_lastLogTime(log_path)
                last_logTime_str = last_logTime.strftime(self.__logTime_format)

                # Check if last log was less than 30 minutes ago
                if datetime.now() < (last_logTime + timedelta_30m):
                    ostelServices_status[service_name] = 'Up', last_logTime_str
                else:
                    ostelServices_status[service_name] = 'Warning', last_logTime_str

                # Check if last log was less than 2 hours ago
                if datetime.now() > (last_logTime + timedelta_180m):
                    ostelServices_status[service_name] = 'Down', last_logTime_str

            return ostelServices_status

        else:
            return 'Ostel services does not exist on this server'


services_checker = ServicesChecker()
