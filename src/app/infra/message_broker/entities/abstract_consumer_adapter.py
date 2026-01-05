import threading
import time
from abc import abstractmethod
from src.app.infra.message_broker.interfaces.consumer_service import ConsumerService


class AbstractConsumerAdapter(ConsumerService):
    """
    Abstract consumer adapter with failsafe polling mechanism.

    Provides thread-safe consumer lifecycle management with:
    - Automatic restart on polling errors
    - Configurable retry delay
    - Clean shutdown handling
    """

    # Configuration
    POLL_RESTART_DELAY_SECONDS = 5  # Wait time before restarting after error

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
        """
        Wrapper to run the polling method with automatic restart on failure.

        Uses a while loop (not recursion) to prevent stack overflow.
        Waits POLL_RESTART_DELAY_SECONDS before restarting after an error.
        """
        while not self.stop_flag.is_set():
            try:
                self.poll_messages()
            except Exception as e:
                if self.stop_flag.is_set():
                    self.logger.info("Poll stopped due to shutdown signal")
                    break
                self.logger.error(
                    f"Error caught in _poll_wrapper: {e}. "
                    f"Restarting in {self.POLL_RESTART_DELAY_SECONDS}s..."
                )
                # Wait before retry, but check stop_flag periodically
                for _ in range(self.POLL_RESTART_DELAY_SECONDS):
                    if self.stop_flag.is_set():
                        break
                    time.sleep(1)

        self.logger.info("Poll wrapper exited gracefully")

    def start_scheduler(self):
        """Start the scheduler in a separate thread."""
        with self.lock:
            if self.thread_list:
                warning_message = "Poll Messages - start scheduler: Already started"
                self.logger.warning(warning_message)
                raise RuntimeError(warning_message)

            try:
                self.stop_flag.clear()  # Reset stop flag for fresh start
                self.before_starting_poll()
                self.scheduler_thread = threading.Thread(
                    target=self._poll_wrapper, daemon=True
                )
                self.scheduler_thread.start()
                self.logger.info("Poll Messages: Start Command")
                self.thread_list.append(self.scheduler_thread)
                self.after_starting_poll()
                return self.scheduler_thread
            except Exception as e:
                self.logger.error(f"Failed to start scheduler: {e}")
                raise RuntimeError(f"Failed to start scheduler: {e}")

    def stop_scheduler(self):
        """Stop the scheduler thread gracefully."""
        with self.lock:
            if not self.thread_list:
                warning_message = "Poll Messages - stop scheduler: Nothing to stop"
                self.logger.warning(warning_message)
                raise RuntimeError(warning_message)

            self.logger.info("Poll Messages: Stop Command initiated")
            self.before_stopping_poll()
            self.stop_flag.set()  # Signal thread to stop

            # Wait for thread to finish with timeout
            for thread in self.thread_list:
                thread.join(timeout=10)
                if thread.is_alive():
                    self.logger.warning(
                        f"Thread {thread.name} did not stop within timeout"
                    )

            self.thread_list = []
            self.after_stopping_poll()
            self.logger.info("Poll Messages: Stop Command completed")
            return self.scheduler_thread

    def is_scheduler_running(self):
        """Check if the scheduler is currently running."""
        with self.lock:
            return len(self.thread_list) > 0
