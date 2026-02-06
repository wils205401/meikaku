class AppBaseException(Exception):
    def __init__(self, message: str, error: str, status_code: int = 400) -> None:
        self.status_code = status_code
        self.error = error
        self.message = message
        super().__init__(message)
