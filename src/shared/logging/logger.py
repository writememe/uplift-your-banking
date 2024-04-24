"""Shared logging module used throughout the project."""

import logging


class InternalLogger:
    """Internal Logger for Cisco Support Toolkit."""

    def __init__(
        self,
        log_level: str,
        log_file_name: str = "log_file_name.log",
        app_name: str = "",
    ) -> None:
        """Initialise a logger object, to be used to perform logging and console outputs to the screen.

        The log_level is passed into the function and used to set
        the logging level.

        Args:
            log_level: The severity logging level for all events.
            log_file_name: The name of the log file (including file extension).
            app_name: The application name used within the log file.

        Returns:
            logger: An initialised Logger object

        Raises:
            N/A
        """
        # If/Else condition to check whether app_name is provided
        if not app_name:  # noqa: SIM108
            # Create a logger object using the standard __name__ convention
            logger = logging.getLogger(__name__)
        else:
            # Create a logger object using the app_name passed into the function.
            logger = logging.getLogger(app_name)
            # Create a logger object
        # Setup the logging formatters for log and stream outputs
        log_fmt = logging.Formatter("%(asctime)s - " "%(levelname)s - " "%(name)s - " "%(message)s")
        stream_fmt = logging.Formatter("%(levelname)s - " "%(name)s - " "%(message)s")
        # Setup file handler and use a different log format for output
        f_handler = logging.FileHandler(log_file_name)
        f_handler.setFormatter(log_fmt)
        # Setup stream handler and use a different log format for output
        s_handler = logging.StreamHandler()
        s_handler.setFormatter(stream_fmt)
        # Create a dictionary of log_level mappings
        logger_map = {
            "INFO": logging.INFO,
            "DEBUG": logging.DEBUG,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        # Set logging level based on the log_level
        # taken from the user using argparse and the log_level dictionary map above
        # NOTE: This will be an integer value
        # https://docs.python.org/3/library/logging.html#logging-levels
        log_integer = logger_map.get(log_level)
        logger.setLevel(level=log_integer)  # type: ignore
        f_handler.setLevel(level=log_integer)  # type: ignore
        s_handler.setLevel(level=log_integer)  # type: ignore
        # Add these handlers to the logger objects
        logger.addHandler(f_handler)
        logger.addHandler(s_handler)
        self.logger = logger

    # Helpful wrapper method to access lower-level logging methods
    # For example, instead of doing InternalLogger.logger.info, we expose InternalLogger.info instead
    def debug(self, string: str) -> None:
        """Wrapper method to perform debug logging.

        Args:
            string: The message to be logged.

        Returns:
            N/A

        Raises:
            N/A
        """
        self.logger.debug(string)

    def info(self, string: str) -> None:
        """Wrapper method to perform informational logging.

        Args:
            string: The message to be logged.

        Returns:
            N/A

        Raises:
            N/A
        """
        self.logger.info(string)

    def warning(self, string: str) -> None:
        """Wrapper method to perform warning logging.

        Args:
            string: The message to be logged.

        Returns:
            N/A

        Raises:
            N/A
        """
        self.logger.warning(string)

    def error(self, string: str) -> None:
        """Wrapper method to perform error logging.

        Args:
            string: The message to be logged.

        Returns:
            N/A

        Raises:
            N/A
        """
        self.logger.error(string)

    def critical(self, string: str) -> None:
        """Wrapper method to perform critical logging.

        Args:
            string: The message to be logged.

        Returns:
            N/A

        Raises:
            N/A
        """
        self.logger.critical(string)


if __name__ == "__main__":
    # Example usage of the InternalLogger
    a = InternalLogger(log_level="DEBUG", log_file_name="abc.log", app_name="hello")
    # This is the way of logging, using the underlying logger method
    a.logger.info("Hello")
    # This is using the "info()" method added onto the InternalLogger class, which provides a "wrapper" around
    # the underlying logger method
    a.info("Hello")
