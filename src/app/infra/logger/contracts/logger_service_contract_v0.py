from src.app.infra.logger.interfaces.logger_service import LoggerService
import logging
from src.app.infra.dotenv.services.service_dotenv import get_service_dotenv

dotenv = get_service_dotenv()


class LoggerServiceContractV0(LoggerService):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")

        file_handler = logging.FileHandler(dotenv.LOG_FILE)
        file_handler.setLevel(logging.ERROR)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

        class bcolors:
            HEADER = "\033[95m"
            OKBLUE = "\033[94m"
            OKCYAN = "\033[96m"
            OKGREEN = "\033[92m"
            WARNING = "\033[93m"
            FAIL = "\033[91m"
            ENDC = "\033[0m"
            BOLD = "\033[1m"
            UNDERLINE = "\033[4m"

        self.bcolors = bcolors

    # DEBUG : Detailed information, typically of interest only when diagnosing problems.
    def debug(self, payload):
        self.logger.debug(self.bcolors.OKBLUE + str(payload) + self.bcolors.ENDC)

    # INFO : Confirmation that things are working as expected.
    def info(self, payload):
        self.logger.info(self.bcolors.OKCYAN + str(payload) + self.bcolors.ENDC)

    # WARNING : An indication that something unexpected happened, or indicative of some problem in the near future. The software is still working as expected.
    def warning(self, payload):
        self.logger.warning(self.bcolors.WARNING + str(payload) + self.bcolors.ENDC)

    # ERROR : Due to a more serious problem, the software has not been able to perform some function.
    def error(self, payload):
        self.logger.error(self.bcolors.FAIL + str(payload) + self.bcolors.ENDC)

    # CRITICAL : A serious error, indicating that the program itself may be unable to continue runnin.
    def critical(self, payload):
        self.logger.critical(self.bcolors.BOLD + str(payload) + self.bcolors.ENDC)
