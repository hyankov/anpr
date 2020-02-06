"""
Description
--
Module providing threading.
"""

# System imports
import queue
import threading
from typing import Any, List


class ConsumerProducer:
    """
    Simple class that consumes input and pushes produced
    output to subscribers.
    """

    def __init__(self, subscribers: List[Any] = [], limit: int = 0):
        """
        Description
        --
        Initializes the instance.

        Parameters
        --
        - subscribers - the list of subscribers to push produced
        items to.
        - limit - the queue limit.
        """

        # See https://docs.python.org/3/library/queue.html
        self.queue = queue.Queue(limit)
        self.stopped = True

        self._subscribers = subscribers
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

    def _produce(self, item: Any) -> Any:
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

        return item

    def _work(self) -> None:
        """
        Description
        --
        Does the work in a thread, until the service is stopped. By default,
        that's processing input items, until service is stopped.
        """

        while not self.stopped:
            # Read the next item, consume it and produce
            result = self._produce(
                        self._consume(
                            self._get_next()))

            # TODO: Different results to different subscribers
            # Publish the result to all subscribers
            if result is not None:
                for subscriber in self._subscribers:
                    try:
                        subscriber.queue.put_nowait(result)
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

        for subscriber in self._subscribers:
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
            for subscriber in self._subscribers:
                subscriber.start()

            # Start the worker in a thread
            self.stopped = False
            if threaded:
                self._thread = threading.Thread(target=self._work)
                self._thread.start()
            else:
                self._work()

        return self
