import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from app import app


def test_home_page():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200


def test_invalid_url():
    client = app.test_client()

    response = client.post(
        "/shorten",
        data={"url": "hello"}
    )

    assert response.status_code == 400


def test_url_not_found():
    client = app.test_client()

    response = client.get("/doesnotexist")

    assert response.status_code == 404
