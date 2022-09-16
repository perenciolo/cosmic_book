from typing import List, Dict, Callable, Type
from allocation.adapters import email
from allocation.domain import events

from allocation.service_layer import unit_of_work

from allocation.service_layer import handlers


def handle(event: events.Event, uow: unit_of_work.AbstractUnitOfWork):
    results = []
    queue = [event]
    while queue:
        event = queue.pop(0)
        for handler in HANDLERS[type(event)]:
            results.append(handler(event, uow=uow))
            queue.extend(uow.collect_new_events())

    return results


def send_out_of_stock_notification(event: events.OutOfStock):
    email.send_mail(
        "stock@made.com",
        f"Out of stock for {event.sku}",
    )


HANDLERS = {
    events.BatchCreated: [handlers.add_batch],
    events.BatchQuantityChanged: [handlers.change_batch_quantity],
    events.OutOfStock: [handlers.send_out_of_stock_notification],
    events.AllocationRequired: [handlers.allocate],
}  # type: Dict[Type[events.Event], List[Callable]]
