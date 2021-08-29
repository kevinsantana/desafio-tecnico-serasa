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
        return str(self.__created_at)

    @property
    def updated_at(self):
        return str(self.__updated_at)

    @created_at.setter
    def created_at(self, created_at: datetime):
        if isinstance(created_at, datetime):
            self.__created_at = created_at

    @updated_at.setter
    def updated_at(self, updated_at: datetime):
        if isinstance(updated_at, datetime):
            self.__updated_at = updated_at

    def dict(self) -> dict:
        new_dict = dict()
        for key, value in self.__dict__.items():
            if value and key.startswith("_Order__"):
                new_dict[key.replace("_Order__", "")] = value
            if not value:
                continue
        return new_dict

    def insert(
        self,
        id: str = str(uuid4()),
        index: str = "orders",
        doc_type: str = "order",
    ):
        """
        Insert.
        """
        if not self.__created_at:
            self.created_at = datetime.utcnow()
        return super().insert(
            document=self.dict(), id=id, index=index, doc_type=doc_type
        )

    def update(
        self,
        id: int,
        index: str = "orders",
        doc_type: str = "order",
    ):
        """
        Update
        """
        if not self.__updated_at:
            self.updated_at = datetime.utcnow()
        return super().update(doc=self.dict(), id=id, index=index, doc_type=doc_type)

    def find_by_id(
        self,
        id: str,
        index: str = "orders",
        doc_type: str = "order",
    ):
        """
        Find by id
        """
        return super().list_one(id, index, doc_type)

    def delete(
        self,
        id: str,
        index: str = "orders",
        doc_type: str = "order",
    ):
        """
        Delete
        """
        return super().delete(id, index, doc_type)

    def find_all(
        self,
        query=None,
        quantity: int = 10,
        page: int = 0,
        index: str = "orders",
        doc_type: str = "order",
    ):
        """
        Find all
        """
        return super().list_all(
            query=query,
            quantity=quantity,
            page=page,
            index=index,
            doc_type=doc_type,
        )

    def __repr__(self):
        return f"{self.__dict__.items()}"
