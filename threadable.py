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

    def _get_next(self) -> Any:
        """
        Description
        --
        Gets the next item. By default, from the queue.
        """

        if not self.queue.empty():
            try:
                # TODO: Multiple workers, but preserve order
                # See https://docs.python.org/3/library/queue.html#queue.Queue.get_nowait
                return self.queue.get_nowait()
                # self.queue.task_done()
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
        The result of processing the item. Will be passed
        to the subscribers.
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

        while not self.stopped:
            time.sleep(0.001)

            # Read the next item, consume it and produce
            results = self._produce(
                        self._consume(
                            self._get_next()))

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
            # Start the subscribers first
            for channel in self._out_channels.keys():
                for subscriber in self._out_channels[channel]:
                    subscriber.start()

            # Start the worker in a thread
            self.stopped = False
            if threaded:
                self._thread = threading.Thread(target=self._work)
                self._thread.start()
            else:
                self._work()

        return self
