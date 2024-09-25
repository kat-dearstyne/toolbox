import time
from typing import Any, Callable, Iterable, List, Optional, Set

from tqdm import tqdm

from toolbox.constants.logging_constants import TQDM_NCOLS
from toolbox.constants.threading_constants import THREAD_SLEEP
from toolbox.infra.t_logging.logger_manager import logger
from toolbox.infra.t_threading.rate_limited_queue import ItemType, RateLimitedQueue

ExceptionHandler = Callable[["MultiThreadState", Exception], bool]


class MultiThreadState:
    def __init__(self, iterable: Iterable, title: str, retries: Set, collect_results: bool = False, max_attempts: int = 3,
                 sleep_time: float = THREAD_SLEEP, rpm: int = None, exception_handlers: List[ExceptionHandler] = None):
        """
        Creates the state to synchronize a multi-threaded job.
        :param iterable: List of items to perform work on.
        :param title: The title of the progress bar.
        :param retries: The indices of the iterable to retry.
        :param collect_results: Whether to collect the results of the jobs.
        :param max_attempts: The maximum number of retries after exception is thrown.
        :param sleep_time: The time to sleep after an exception has been thrown.
        :param rpm: Maximum rate of items per minute.
        :param exception_handlers: Can be used to perform special logic when certain exceptions are thrown.
        """
        self.title = title
        self.iterable = list(enumerate(iterable))
        self.result_list = [None] * len(iterable)
        self.item_queue = RateLimitedQueue(rpm)
        self.progress_bar = None
        self.successful: bool = True
        self.exception: Optional[Exception] = None
        self.failed_responses: Set[int] = set()
        self.results: Optional[List[Any]] = None
        self.collect_results = collect_results
        self.sleep_time = sleep_time
        self.max_attempts = max_attempts
        self.exception_handlers = exception_handlers if exception_handlers else []
        self._init_retries(retries)
        self._init_progress_bar()

    def add_work(self, item: ItemType) -> None:
        """
        Adds work to the queue.
        :param item: Item to add.
        :return: None.
        """
        self.item_queue.put(item)

    def get_work(self) -> Any:
        """
        :return: Whether there is work to be performed and its still valid to do so.
        """
        return self.item_queue.get()

    def should_attempt_work(self, attempts: int) -> bool:
        """
        Decides whether a child thread should attempt to perform work.
        :param attempts: The number of attempts at performing the work.
        :return: Whether to try to perform work again.
        """
        return self.below_attempt_threshold(attempts) and self.successful

    def below_attempt_threshold(self, attempts: int) -> bool:
        """
        Whether the number of attempts is below the max threshold.
        :param attempts: The number of attempts at performing work.
        :return: Whether the threshold is exceeded.
        """
        return attempts < self.max_attempts

    def get_item(self) -> Any:
        """
        :return: Returns the next work item.
        """
        return self.item_queue.get()

    def on_item_finished(self, result: Any, index: int) -> None:
        """
        Process the result performed by a job.
        :param result: The result of a job.
        :param index: The index of the item that was processed.
        :return: None
        """
        if self.collect_results:
            assert index is not None, "Expected index to be provided when collect results is activated."
            if result:
                self.result_list[index] = result
        if self.progress_bar is not None:
            self.progress_bar.update()

    def on_exception(self, e: Exception, attempts: int = None, index: int = None) -> bool:
        """
        Handles exception happening in child thread.
        :param e: The exception occurring.
        :param attempts: The number of attempts the child has attempted.
        :param index: The child index (also a unique identifier).
        :return: Whether the exception was handled or not.
        """
        self.item_queue.pause()
        for exception_handler in self.exception_handlers:
            is_handled = exception_handler(self, e, sleep_time=self.sleep_time)
            if is_handled:
                self.item_queue.unpause()
                return True

        if attempts is not None and self.below_attempt_threshold(attempts):
            logger.exception(e)
            logger.info(f"Request failed, retrying in {self.sleep_time} seconds.")
            time.sleep(self.sleep_time)
        else:
            self.successful = False
            self.exception = e
            if index:
                self._record_failure(e, index)
        self.item_queue.unpause()
        return False

    def add_time(self, seconds: float) -> None:
        """
        Increases the interval to wait between items in queue.
        :param seconds: Number of seconds to increase the interval by.
        :return: None
        """
        self.item_queue.change_time_per_request(seconds)
        logger.info(f"Increased time-between-requests to {self.item_queue.time_between_requests} seconds.")

    def _init_progress_bar(self) -> None:
        """
        Initializes the progress bar for the job.
        :return: None
        """
        self.progress_bar = tqdm(total=len(self.item_queue), desc=self.title, ncols=TQDM_NCOLS) if len(self.item_queue) > 0 else None

    def _init_retries(self, retries: Set) -> None:
        """
        Initializes the indices to retry.
        :param retries: The indices to retry.
        :return: None
        """
        for i, item in self.iterable:
            if not retries or i in retries:
                self.item_queue.put((i, item))

    def _record_failure(self, e: Exception, index: int) -> None:
        """
        Saves the exception to failed responses.
        :param e: The error that occurred.
        :param index: Index corresponding to the work that failed.
        :return: None.
        """
        self.failed_responses.add(index)
        if self.collect_results:
            self.result_list[index] = e
