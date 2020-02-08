"""
Description
--
Module providing threading.
"""

# System imports
import queue
import threading
import time
from typing import Any, Dict, List


class WorkerPipe:
    """
    Simple class that consumes input and pushes produced
    output to subscribers.
    """

    channel_main = ''

    def __init__(self, limit: int = 0):
        """
        Description
        --
        Initializes the instance.

        Parameters
        --
        - limit - the queue limit.
        """

        # See https://docs.python.org/3/library/queue.html
        self.queue = queue.Queue(1)  # Size 1, until we start the worker

        self._out_channels = {}  # type: Dict[str, List[Any]]
        self._queue_limit = limit
        self._thread = None  # type: threading.Thread
        self._main_loop_breaker = "##thread circuit breaker##"  # queue circut breaker
        self._stop_requested = False

        # Whether the queue reading is blocking and if it's not, how long
        # to sleep before polling.
        self._is_polling_queue = False
        self._main_loop_sleep = 0.01

    def _get_next_job(self) -> Any:
        """
        Description
        --
        Gets the next job, from a queue. Whether it's blocking
        while waiting for a job or not depends on `self._is_polling_queue`
        """

        if self._stop_requested:
            # Immediately return a loop breaker
            return self._main_loop_breaker

        try:
            if not self._is_polling_queue:
                # Non-polling queue
                return self.queue.get(timeout=1)
            else:
                # Polling queue
                # See https://docs.python.org/3/library/queue.html#queue.Queue.get_nowait
                return self.queue.get_nowait()
        except queue.Empty:
            # Queue is empty
            pass

    def _consume(self, item: Any) -> Any:
        """
        Description
        --
        Consumes a work item.

        Parameters
        --
        - item - the item to consume.

        Returns
        --
        The result of the consumption of the item, if any.
        """

        return item

    def _produce(self, item: Any) -> Dict[str, Any]:
        """
        Description
        --
        Produces an output, based on the consumed input.

        Parameters
        --
        - item - the consumed item to process.

        Returns
        --
        Results on different channels, to be routed to the
        subscribers of those channels. By default, returns on
        the main channel.
        """

        # return through the default channel
        return {self.channel_main: item}

    def _work(self) -> None:
        """
        Description
        --
        Does the work in a thread, until the service is stopped. By default,
        that's processing input items, until service is stopped.
        """

        # Clear the queue
        self.queue = queue.Queue(self._queue_limit)

        # The service started
        self._service_started()

        # *** MAIN THREAD LOOP ***
        # Encountering `_main_loop_breaker` will break us out and effectively
        # end the thread.
        for job in iter(self._get_next_job, self._main_loop_breaker):
            # Consume the input job and produce output jobs
            results = self._produce(self._consume(job))

            if self._out_channels and results is not None:
                # Publish the non-None result to all subscribers
                for r_channel in results.keys():
                    if r_channel in self._out_channels.keys():
                        for subscriber in self._out_channels[r_channel]:
                            result = results[r_channel]
                            if result is not None:
                                try:
                                    subscriber.receive(result)
                                except queue.Full:
                                    pass

            # Sleep before polling again
            time.sleep(self._main_loop_sleep)

        # The service stopped
        self._service_stopped()
        self._stop_requested = False

    def _service_stopped(self) -> None:
        """
        Description
        --
        Override.
        Called when the service is stopped.
        """

        print(self.__class__.__name__, "service stopped")

    def _service_started(self) -> None:
        """
        Description
        --
        Override.
        Called when the service is started.
        """

        pass

    def wait_to_finish(self):
        """
        Description
        --
        Waits for the thread to finish (blocking).
        """

        # Finish the thread
        if self._thread is not None:
            self._thread.join()

            # Indicate we can start again
            self._thread = None

            print(self.__class__.__name__, "thread joined")

    def link_to(self, recipient: Any, channel: str = None) -> Any:
        """
        Description
        --
        Link the `channel` output of the pipe to `recipient`. The
        `recupient` object must have a method `receive`, to receive
        the output of this pipe. Ideally, this is another worker pipe.

        Parameters
        --
        - recipient - the object which will receive the channel
        output of this pipe.
        - channel - the output channel of this pipe, which we link to
        the `recipient`. If none specified, it will be the default,
        main channel.

        Returns
        --
        Self, for fluent API.
        """

        if not recipient:
            raise ValueError("recipient is required!")
        else:
            receive_method = getattr(recipient, "receive", None)
            if not callable(receive_method):
                raise ValueError("recipient must have a receive() method")

        if not channel:
            channel = self.channel_main

        if channel not in self._out_channels:
            self._out_channels[channel] = []

        self._out_channels[channel].append(recipient)

        return self

    def receive(self, job) -> None:
        """
        Description
        --
        Receive input job.

        Parameters
        --
        - job - the received input job.
        """

        self.queue.put_nowait(job)

    def stop(self) -> None:
        """
        Description
        --
        Stops the worker pipe.
        """

        if not self._stop_requested:
            # Signal breaking the loop
            self._stop_requested = True

            # Wait for the thread to finish
            self.wait_to_finish()

    def start(self) -> Any:
        """
        Description
        --
        Start the worker pipe.

        Returns
        --
        Self, for fluent API.
        """

        if self._thread:
            # The service wasn't started, seems to be already
            # started.
            return False

        # Start doing work, in separate thread
        self._thread = threading.Thread(target=self._work)
        self._thread.start()

        # The service was started
        return self
