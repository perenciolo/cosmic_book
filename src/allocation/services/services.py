from typing import Optional
from datetime import date

from allocation.domain import model, OrderLine, Batch, Sku, Quantity, Reference
from allocation.adapters import AbstractRepository


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def add_batch(
    ref: Reference,
    sku: Sku,
    qty: Quantity,
    eta: Optional[date],
    repo: AbstractRepository,
    session,
) -> None:
    repo.add(batch=model.Batch(ref, sku, qty, eta))
    session.commit()


def allocate(line: OrderLine, repo: AbstractRepository, session) -> str:
    batches = repo.list()

    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid sku {line.sku}")

    batchref = model.allocate(line, batches)
    session.commit()

    return batchref


def deallocate(
    line: OrderLine, repo: AbstractRepository, session, reference: model.Reference
) -> None:
    batch = repo.get(reference=reference)

    if not is_valid_sku(line.sku, [batch]):
        raise InvalidSku(f"Invalid sku {line.sku}")

    return model.deallocate(line, batch)
