import pytest

from app import create_app


@pytest.fixture(scope='module')
def client():
    flask_app = create_app()

    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = flask_app.test_client()

    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()


def test_home_page(client):
    response = client.get('/tips')
    assert response.status_code == 200
