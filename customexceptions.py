class ValidationError(Exception):
    def __init__(self, message, errors=None) -> None:
        super().__init__(message)
        self.message = message
        self.errors = errors


class MongoError(Exception):
    def __init__(self, message, errors=None) -> None:
        super().__init__(message)
        self.message = message
        self.errors = errors


class LoggerError(Exception):
    def __init__(self, message, errors=None) -> None:
        super().__init__(message)
        self.message = message
        self.errors = errors