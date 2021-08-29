from order_api.exceptions import OrderApiException


class QueryMalformedException(OrderApiException):
    def __init__(
        self,
        status: int,
        error: str,
        message: str,
        error_details: list = [],
    ):
        self.status = status
        self.error = error
        self.message = message
        self.error_details = error_details
        super().__init__(status, error, message, error_details)


class DatabaseException(OrderApiException):
    def __init__(
        self,
        status: int,
        error: str,
        message: str,
        error_details: list = [],
    ):
        self.status = status
        self.error = error
        self.message = message
        self.error_details = error_details
        super().__init__(status, error, message, error_details)
