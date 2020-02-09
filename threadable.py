"""
Description
--
Module providing threading.
"""

from __future__ import annotations

# System imports
import queue
import threading
import time
from typing import Any, Dict, List

# Local imports
import logger as log


class WorkerPipe:
    """
    A worker 'pipe' that consumes input and pushes produced
    output to other pipes.
    """

    channel_main = 'channel_main'

    def __init__(self, jobs_limit: int = 0):
        """
        Description
        --
        Initializes the instance.

        Parameters
        --
        - jobs_limit - the queue limit.
        """

        self._logger = log.get_module_logger(self.__class__.__name__)

        # See https://docs.python.org/3/library/queue.html
        self.queue = queue.Queue(jobs_limit)

        # Connections to other pipes/receivers
        self._recipients = {}  # type: Dict[str, List[Any]]

        self._wait_for_job_s = 1  # How long to wait for a job. 0 for no waiting.
        self._main_loop_sleep_s = 0.02  # Give other threads a breather
        self._main_loop_sentry = "##thread circuit breaker##"  # queue circut breaker
        self._main_loop_break_requested = False  # When true, main loop will get sentry
        self._thread = None  # type: threading.Thread

    def _get_next_job(self) -> Any:
        """
        Description
        --
        Gets the next job, from a queue.
        """

        # Is the loop breaker tripped?
        if self._main_loop_break_requested:
            self._logger.debug("Yielding main loop breaker")

            # Immediately return a loop breaker
            return self._main_loop_sentry

        try:
            if not self._wait_for_job_s:
                # Not waiting for a job
                # See https://docs.python.org/3/library/queue.html#queue.Queue.get_nowait
                return self.queue.get_nowait()
            else:
                # Waiting for a job, maximum of X seconds
                return self.queue.get(timeout=self._wait_for_job_s)
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

    def _main_loop(self) -> None:
        """
        Description
        --
        Does the work in a thread, until the service is stopped.
        """

        # Clear the queue
        self.queue = queue.Queue(self.queue.maxsize)

        # The main loop is about the start
        self._logger.debug("On start")
        self._on_starting()
        self._logger.debug("Main loop starting")

        # *** MAIN LOOP ***
        # Encountering `_main_loop_breaker` will break us out and effectively
        # end the thread.
        for job in iter(self._get_next_job, self._main_loop_sentry):
            # Consume the input job and produce output jobs
            results = self._produce(self._consume(job))

            # Propagate result to subscribers
            if self._recipients and results is not None:
                # Publish the non-None result to all recipients
                for r_channel in results.keys():
                    if r_channel in self._recipients.keys():
                        for recipient in self._recipients[r_channel]:
                            result = results[r_channel]
                            if result is not None:
                                try:
                                    recipient.receive(result)
                                except queue.Full:
                                    pass

            # Sleep before next job, to give other threads a chance
            time.sleep(self._main_loop_sleep_s)

        # The main loop ended
        self._logger.debug("On stopped")
        self._on_stopped()
        self._logger.debug("Main loop stopped")

    def _on_starting(self) -> None:
        """
        Description
        --
        Override.
        Called before the main loop.
        """

        pass

    def _on_stopped(self) -> None:
        """
        Description
        --
        Override.
        Called after the main loop.
        """

        pass

    def link_to(self, recipient: WorkerPipe, channel: str = None) -> WorkerPipe:
        """
        Description
        --
        Link the `channel` output of the pipe to `recipient`.

        Parameters
        --
        - recipient - the pipe which will receive the channel
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

        if not channel:
            channel = self.channel_main

        if channel not in self._recipients:
            self._recipients[channel] = []

        self._recipients[channel].append(recipient)
        self._logger.debug("Subscribed {} on channel '{}'".format(recipient, channel))

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

    def start(self, blocking=False) -> WorkerPipe:
        """
        Description
        --
        Starts the service.

        Parameters
        --
        - blocking - wait for the thread to finish.

        Returns
        --
        Self, for fluent API.
        """

        self._logger.debug("Service start")

        # Reset the breaker
        self._main_loop_break_requested = False

        # Start the main loop in a separate thread
        self._thread = threading.Thread(target=self._main_loop)
        # self._thread.daemon = True  # See https://stackoverflow.com/a/190017/253266
        self._thread.start()

        if blocking:
            # Wait for the thread to finish
            self._logger.debug("Thread joining ...")
            self._thread.join()
            self._logger.debug("Thread joined")

        return self

    def stop(self) -> WorkerPipe:
        """
        Description
        --
        Stops the service.

        Returns
        --
        Self, for fluent API.
        """

        self._logger.debug("Service stop")

        # Signal breaking the loop
        self._main_loop_break_requested = True

        return self
