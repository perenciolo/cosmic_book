from __future__ import annotations

from typing import TYPE_CHECKING

from allocation.adapters import email
from allocation.domain import (
    AllocationRequired,
    BatchCreated,
    BatchQuantityChanged,
    OutOfStock,
)
from allocation.domain.model import Batch, OrderLine, Product

from . import messagebus

if TYPE_CHECKING:
    from . import unit_of_work


class InvalidSku(Exception):
    pass


def add_batch(
    event: BatchCreated,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:

        product = uow.products.get(sku=event.sku)

        if product is None:
            product = Product(event.sku, batches=[])
            uow.products.add(product)

        product.batches.append(Batch(event.ref, event.sku, event.qty, event.eta))
        uow.commit()


def allocate(
    event: AllocationRequired,
    uow: unit_of_work.AbstractUnitOfWork,
) -> str:
    line = OrderLine(event.orderid, event.sku, event.qty)

    with uow:
        product = uow.products.get(sku=line.sku)

        if product is None:
            raise InvalidSku(f"Invalid sku {line.sku}")

        batchref = product.allocate(line)

        uow.commit()
        return batchref


def change_batch_quantity(
    event: BatchQuantityChanged,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        product = uow.products.get_by_batchref(batchref=event.ref)
        product.change_batch_quantity(ref=event.ref, qty=event.qty)
        uow.commit()


def send_out_of_stock_notification(
    event: OutOfStock,
    uow: unit_of_work.AbstractUnitOfWork,
):
    email.send_mail("stock@made.com", f"Out of stock fr {event.sku}")
