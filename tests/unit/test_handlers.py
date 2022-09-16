from datetime import date

from allocation.domain import events, commands
from allocation.service_layer.messagebus import MessageBus
from tests.unit.mocks import FakeMessageBus, FakeUnitOfWork


class TestAddBatch:
    def test_add_batch_for_new_product(self):
        uow = FakeUnitOfWork()
        messagebus = MessageBus(uow)
        messagebus.handle(commands.CreateBatch("b1", "CRUNCHY-ARMCHAIR", 100, None))
        assert uow.products.get("CRUNCHY-ARMCHAIR") is not None
        assert uow.committed


class TestAllocate:
    def test_allocate_returns_allocation(self):
        uow = FakeUnitOfWork()
        messagebus = MessageBus(uow)
        messagebus.handle(
            commands.CreateBatch("batch1", "COMPLICATED-LAMP", 100, None),
        )
        messagebus.handle(
            commands.Allocate("o1", "COMPLICATED-LAMP", 10),
        )
        batches = uow.products.get(sku="COMPLICATED-LAMP").batches

        assert len(batches) == 1
        assert batches[0].reference == "batch1"


class TestChangeBatchQuantity:
    def test_changes_available_quantity(self):
        uow = FakeUnitOfWork()
        messagebus = MessageBus(uow)
        messagebus.handle(commands.CreateBatch("batch1", "ADORABLE-SETTEE", 100, None))
        [batch] = uow.products.get(sku="ADORABLE-SETTEE").batches
        assert batch.available_quantity == 100

        messagebus.handle(commands.ChangeBatchQuantity("batch1", 50))

        assert batch.available_quantity == 50

    # def test_reallocates_if_necessary(self):
    #     uow = FakeUnitOfWork()
    #     messagebus = MessageBus(uow)
    #     event_history = [
    #         commands.CreateBatch("batch1", "INDIFFERENT-TABLE", 50, None),
    #         commands.CreateBatch("batch2", "INDIFFERENT-TABLE", 50, date.today()),
    #         commands.Allocate("order1", "INDIFFERENT-TABLE", 20),
    #         commands.Allocate("order2", "INDIFFERENT-TABLE", 20),
    #     ]
    #
    #     for e in event_history:
    #         messagebus.handle(e)
    #
    #     [batch1, batch2] = uow.products.get(sku="INDIFFERENT-TABLE").batches
    #     assert batch1.available_quantity == 10
    #     assert batch2.available_quantity == 50
    #
    #     messagebus.handle(commands.ChangeBatchQuantity("batch1", 25))
    #
    #     # order1 or order2 will be deallocated, so we'll have 25 - 20
    #     assert batch1.available_quantity == 5
    #     # and 20 will be reallocated to the next batch
    #     assert batch2.available_quantity == 30

    def test_reallocates_if_necessary_isolated(self):
        uow = FakeUnitOfWork()
        messagebus = FakeMessageBus(uow)
        # test setup as before
        event_history = [
            commands.CreateBatch("batch1", "INDIFFERENT-TABLE", 50, None),
            commands.CreateBatch("batch2", "INDIFFERENT-TABLE", 50, date.today()),
            commands.Allocate("order1", "INDIFFERENT-TABLE", 20),
            commands.Allocate("order2", "INDIFFERENT-TABLE", 20),
        ]
        [messagebus.handle(e) for e in event_history]

        assert messagebus.events_published == event_history

        messagebus.handle(commands.ChangeBatchQuantity("batch1", 25))

        assert messagebus.events_published[-1] == commands.ChangeBatchQuantity(
            "batch1", 25
        )
