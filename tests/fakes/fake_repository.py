from typing import List

from allocation.adapters import AbstractRepository
from allocation.domain import model


class FakeRepository(AbstractRepository):
    def __init__(self, batches: List[model.Batch]):
        self._batches = set(batches)

    def add(self, batch: model.Batch):
        self._batches.add(batch)

    def get(self, reference: model.Reference):
        return next(b for b in self._batches if b.reference == reference)

    def list(self):
        return list(self._batches)

    @staticmethod
    def for_batch(ref, sku, qty, eta=None):
        return FakeRepository(
            [
                model.Batch(ref, sku, qty, eta),
            ]
        )
