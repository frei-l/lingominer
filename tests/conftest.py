from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from lingominer.app import app
from lingominer.models.user import User


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app, headers={"Authorization": "Bearer test"}) as c:
        yield c


@pytest.fixture(scope="module")
def example_user():
    user = User(id="test", name="test")
    yield user

