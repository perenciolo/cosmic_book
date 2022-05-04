import abc
from typing import List

from allocation.domain import model


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: model.Batch) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference: model.Reference) -> model.Batch:
        raise NotImplementedError

    @abc.abstractmethod
    def list(self):
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, batch: model.Batch) -> None:
        self.session.add(batch)

    def get(self, reference: model.Reference) -> model.Batch:
        return self.session.query(model.Batch).filter_by(reference=reference).first()

    def list(self) -> List[model.Batch]:
        return self.session.query(model.Batch).all()


class FakeRepository(AbstractRepository):
    def __init__(self, batches: List[model.Batch]):
        self._batches = set(batches)

    def add(self, batch: model.Batch):
        self._batches.add(batch)

    def get(self, reference: model.Reference):
        return next(b for b in self._batches if b.reference == reference)

    def list(self):
        return list(self._batches)
