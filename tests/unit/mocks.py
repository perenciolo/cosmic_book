from allocation.adapters import repository
from allocation.domain import events
from allocation.service_layer import handlers, messagebus, unit_of_work


class FakeRepository(repository.AbstractRepository):
    def __init__(self, products):
        super().__init__()
        self._products = set(products)

    def _add(self, product):
        self._products.add(product)

    def _get(self, sku):
        return next((p for p in self._products if p.sku == sku), None)

    def _get_by_batchref(self, batchref):
        return next(
            (p for p in self._products for b in p.batches if b.reference == batchref),
            None,
        )


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.products = FakeRepository([])
        self.committed = False

    def _commit(self):
        self.committed = True

    def rollback(self):
        pass


class FakeMessageBus(messagebus.AbstractMessageBus):
    def __init__(self, uow: unit_of_work.AbstractUnitOfWork):
        super(FakeMessageBus, self).__init__(uow)
        self.events_published = []
        self.HANDLERS = {
            events.BatchCreated: [self.mock_event_handler],
            events.BatchQuantityChanged: [self.mock_event_handler],
            events.OutOfStock: [self.mock_event_handler],
            events.AllocationRequired: [self.mock_event_handler],
        }

    def mock_event_handler(self, e, uow: unit_of_work.AbstractUnitOfWork):
        self.events_published.append(e)
