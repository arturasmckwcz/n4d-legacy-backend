import pytest
import requests

from tests_e2e.test_endpoints.variables import ALFRED_API_URL

SCHEMA_URL = f"{ALFRED_API_URL}/api"


@pytest.mark.parametrize(
    "url",
    [
        f"{ALFRED_API_URL}/",
        f"{SCHEMA_URL}/schema/swagger-ui",
        f"{SCHEMA_URL}/schema/redoc",
        f"{SCHEMA_URL}/schema",
    ],
)
def test_schema_ok(url):
    schema_request = requests.get(url)
    assert schema_request.ok is True
