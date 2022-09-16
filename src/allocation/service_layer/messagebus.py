from typing import List, Dict, Callable, Type
from allocation.domain import events

from allocation.service_layer import unit_of_work

from allocation.service_layer import handlers


class AbstractMessageBus:
    HANDLERS: Dict[Type[events.Event], List[Callable]]

    def __init__(self, uow: unit_of_work.AbstractUnitOfWork):
        self.uow = uow

    def handle(self, event: events.Event):
        for handler in self.HANDLERS[type(event)]:
            handler(event, uow=self.uow)


class MessageBus(AbstractMessageBus):
    HANDLERS = {
        events.BatchCreated: [handlers.add_batch],
        events.BatchQuantityChanged: [handlers.change_batch_quantity],
        events.OutOfStock: [handlers.send_out_of_stock_notification],
        events.AllocationRequired: [handlers.allocate],
    }  # type: Dict[Type[events.Event], List[Callable]]
