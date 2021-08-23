from uuid import uuid4


class ErrorDetails:
    def __init__(self, message: str, unique_id: str = str(uuid4())):
        self.message = message
        self.unique_id = unique_id

    def to_dict(self):
        return {"unique_id": self.unique_id, "message": self.message}


class UserApiException(Exception):  # pragma: no cover
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
