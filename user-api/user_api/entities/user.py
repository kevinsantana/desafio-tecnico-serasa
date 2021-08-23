from dataclasses import dataclass

from user_api.database.user import User as UserDB


@dataclass()
class User(UserDB):
    def to_object(self):  # pragma: no cover
        return User(**self.to_dict())

    def __repr__(self) -> str:
        return f"{self.to_dict()}"
