from uuid import uuid4
from datetime import datetime

from order_api.database import Database


class Order(Database):
    def __init__(
        self,
        user_id: int = None,
        item_description: str = None,
        item_quantity: int = None,
        item_price: float = None,
        total_value: float = None,
        created_at: str = None,
        updated_at: str = None,
    ):
        self.__user_id = user_id
        self.__item_description = item_description
        self.__item_quantity = item_quantity
        self.__item_price = item_price
        self.__total_value = total_value
        self.__created_at = created_at
        self.__updated_at = updated_at

    @property
    def user_id(self):
        return self.__user_id

    @property
    def item_description(self):
        return self.__item_description

    @property
    def item_quantity(self):
        return self.__item_quantity

    @property
    def item_price(self):
        return self.__item_price

    @property
    def total_value(self):
        return self.__total_value

    @property
    def created_at(self):
        return self.__created_at

    @property
    def updated_at(self):
        return self.__updated_at

    @created_at.setter
    def created_at(self):
        self.__created_at = datetime.utcnow()

    def dict(self, no_id: bool = False, no_version: bool = False) -> dict:
        new_dict = dict()
        for key, value in self.__dict__.items():
            if no_id and key.startswith("_id"):
                continue
            if no_version and key.startswith("_version"):
                continue
            if key not in {"_id", "_version"} and key.startswith("_"):
                continue
            new_dict[key] = value
        return new_dict

    def insert(
        self,
        type: str,
        id: str = str(uuid4()),
        index: str = "orders",
        doc_type: str = "order",
    ):
        if type not in {"create", "update"}:
            raise ValueError("Metodo nao permitido")
        if not self.__created_at:
            self.created_at = self.created_at
        insertion = super().insert(
            document=self,
            id=id,
            index=index,
            doc_type=doc_type
        ).dict()
        return insertion.get("_id") if type == "create" else insertion.get("version")

    def __repr__(self):
        return f"{self.__dict__.items()}"
