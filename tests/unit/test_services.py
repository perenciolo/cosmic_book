import pytest
from allocation.services import services

from tests.fakes import FakeRepository, FakeSession
from allocation.domain import OrderLine, Batch


def test_returns_allocation():
    sku = "COMPLICATED-LAMP"
    line = OrderLine("o1", sku, 10)
    repo = FakeRepository.for_batch("batch1", sku, 100)

    result = services.allocate(line, repo, FakeSession())

    assert result == "batch1"


def test_error_for_invalid_sku():
    line = OrderLine("o1", "NONEXISTENTSKU", 10)
    batch = Batch("b1", "REALSKU", 100, eta=None)
    repo = FakeRepository([batch])

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate(line, repo, FakeSession())


def test_commits():
    sku = "OMINOUS-MIRROR"
    line = OrderLine("o1", sku, 10)
    batch = Batch("b1", sku, 100, eta=None)
    repo = FakeRepository([batch])
    session = FakeSession()

    services.allocate(line, repo, session)
    assert session.committed is True


def test_add_batch():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, repo, session)
    assert repo.get("b1") is not None
    assert session.committed


def test_allocate_returns_allocation():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("batch1", "COMPLICATED-LAMP", 100, None, repo, session)
    line = OrderLine("o1", "COMPLICATED-LAMP", 10)
    result = services.allocate(line, repo, session)
    assert result == "batch1"


def test_allocate_errors_for_invalid_sku():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "AREALSKU", 100, None, repo, session)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate(OrderLine("o1", "NONEXISTENTSKU", 10), repo, FakeSession())
