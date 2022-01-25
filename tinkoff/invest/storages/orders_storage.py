from abc import ABC
from typing import Dict, Iterable, Tuple

from tinkoff.invest.schemas import OrderState
from tinkoff.invest.storages.item_storage import IItemStorage


class IOrdersStorage(IItemStorage[str, OrderState], ABC):
    pass


class OrdersStorage(IOrdersStorage):
    def __init__(self):
        self._orders: Dict[str, OrderState] = {}

    def items(self) -> Iterable[Tuple[str, OrderState]]:
        pass

    def get(self, item_id: str) -> OrderState:
        pass

    def set(self, item_id: str, new_item: OrderState) -> None:
        pass

    def delete(self, item_id: str) -> None:
        pass
