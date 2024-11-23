"""
This module contains custom exceptions that can be raised by the bot.
"""
class ValidationError(Exception):
    """
    This class represents a validation error.
    """
    def __init__(self, message, errors=None) -> None:
        """
        Initializes a new Exception with the provided error message.

        Args:
            message (str): The error message.
            errors (Optional[List[str]]): A list of error messages.

        Returns:
            None
        """
        super().__init__(message)
        self.message = message
        self.errors = errors


class MongoError(Exception):
    """
    This class represents a mongo error.
    """
    def __init__(self, message, errors=None) -> None:
        """
        Initializes a new Exception with the provided error message.

        Args:
            message (str): The error message.
            errors (Optional[List[str]]): A list of error messages.

        Returns:
            None
        """
        super().__init__(message)
        self.message = message
        self.errors = errors


class LoggerError(Exception):
    """
    This class represents a logger error.
    """
    def __init__(self, message, errors=None) -> None:
        """
        Initializes a new Exception with the provided error message.

        Args:
            message (str): The error message.
            errors (Optional[List[str]]): A list of error messages.

        Returns:
            None
        """
        super().__init__(message)
        self.message = message
        self.errors = errors
