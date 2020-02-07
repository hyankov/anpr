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


class ConsumerProducer:
    """
    Simple class that consumes input and pushes produced
    output to subscribers.
    """

    channel_main = ''

    def __init__(self, out_channels: Dict[str, List[Any]] = None, limit: int = 0):
        """
        Description
        --
        Initializes the instance.

        Parameters
        --
        - out_channels - subscriber channels, to push results to.
        - limit - the queue limit.
        """

        # See https://docs.python.org/3/library/queue.html
        self.queue = queue.Queue(limit)
        self.stopped = True

        self._out_channels = out_channels or {self.channel_main: []}
        self._thread = None  # type: threading.Thread
        self._sentinel = "##thread circuit breaker##"  # queue circut breaker
        self._is_blocking = True
        self._non_blocking_thread_sleep = 0.02

    def _get_next(self) -> Any:
        """
        Description
        --
        Gets the next item. By default, from the queue.
        """

        # See https://docs.python.org/3/library/queue.html#queue.Queue.get_nowait

        # The service has stopped, signal kill the main loop
        if self.stopped:
            return self._sentinel

        if self._is_blocking:
            # Blocking get
            return self.queue.get()
        else:
            # Non-blocking get
            try:
                return self.queue.get_nowait()
            except queue.Empty:
                # Queue is empty
                time.sleep(self._non_blocking_thread_sleep)

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

        # *** MAIN THREAD LOOP ***
        # Encountering `_sentinel` will break us out.
        for job in iter(self._get_next, self._sentinel):
            # Consume the input job and produce output jobs
            results = self._produce(self._consume(job))

            if self._out_channels and results is not None:
                # Publish the result to all subscribers
                for r_channel in results.keys():
                    if r_channel in self._out_channels.keys():
                        for subscriber in self._out_channels[r_channel]:
                            try:
                                subscriber.queue.put_nowait(results[r_channel])
                            except queue.Full:
                                pass

        # The service stopped
        self._service_stopped()

    def _service_stopped(self) -> None:
        """
        Description
        --
        Called when the service is stopped. Override.
        """

        # TODO: Empty queue?
        pass

    def stop(self) -> None:
        """
        Description
        --
        Stops processing queued work items.
        """

        if not self.stopped:
            self.stopped = True

            # Stop the subscribers first
            for channel in self._out_channels.keys():
                for subscriber in self._out_channels[channel]:
                    subscriber.stop()

            if self._thread:
                self._thread.join()

    def start(self, threaded=True) -> Any:
        """
        Description
        --
        Starts processing queued work items.
        """

        if self.stopped:
            # Start the worker in a thread
            self.stopped = False

            # Start the subscribers first
            for channel in self._out_channels.keys():
                for subscriber in self._out_channels[channel]:
                    subscriber.start()

            if threaded:
                self._thread = threading.Thread(target=self._work)
                self._thread.start()
            else:
                self._work()

        return self
