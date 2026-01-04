import threading
from abc import abstractmethod
import traceback
from src.app.infra.message_broker.interfaces.consumer_service import ConsumerService


class AbstractConsumerAdapter(ConsumerService):

    def __init__(self, logger):
        self.logger = logger
        self.lock = threading.Lock()  # Lock for thread safety
        self.stop_flag = threading.Event()  # Flag to signal the thread to stop
        self.thread_list = []

    @abstractmethod
    def before_starting_poll(self):
        pass

    @abstractmethod
    def after_starting_poll(self):
        pass

    @abstractmethod
    def poll_messages(self):
        pass

    @abstractmethod
    def before_stopping_poll(self):
        pass

    @abstractmethod
    def after_stopping_poll(self):
        pass

    def _poll_wrapper(self):
        """Wrapper to run the polling method and handle exceptions."""
        try:
            self.poll_messages()
        except Exception as e:
            self.logger.error(f"Error caught in _poll_wrapper : {e}")
            self._poll_wrapper()

    def start_scheduler(self):
        """Start the scheduler in a separate thread."""
        try:
            if self.thread_list == []:
                self.before_starting_poll()
                self.scheduler_thread = threading.Thread(
                    target=self._poll_wrapper, daemon=True
                )
                self.scheduler_thread.start()
                self.logger.info("Poll Messages : Start Command")
                self.thread_list.append(self.scheduler_thread)
                self.logger.info(self.thread_list)
                self.after_starting_poll()
                return self.scheduler_thread
            else:
                warning_message = "Poll Messages - start scheduler : Already started"
                self.logger.warning(warning_message)
                raise Exception(warning_message)
        except Exception as e:
            raise Exception(f"some problem in start_scheduler : {e}")

    def stop_scheduler(self):
        """Stop the scheduler thread."""
        if self.thread_list != []:
            self.before_stopping_poll()
            self.stop_flag.set()  # Set the stop flag
            self.scheduler_thread.join()  # Wait for the scheduler thread to finish
            self.logger.info("Poll Messages : Stop Command")
            self.logger.info(self.scheduler_thread)
            for threads in self.thread_list:
                threads.join()
            self.thread_list = []
            self.after_stopping_poll()
            return self.scheduler_thread
        else:
            warning_message = "Poll Messages - stop scheduler : Nothing to stop"
            self.logger.warning(warning_message)
            raise Exception(warning_message)

    def is_scheduler_running(self):
        if len(self.thread_list) > 0:
            return True
        else:
            return False
