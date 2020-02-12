import pytest

from app import create_app, db
from app.models import User


@pytest.fixture(scope='module')
def client():
    flask_app = create_app()

    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = flask_app.test_client()

    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(flask_app)

    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    with flask_app.app_context():
        db.create_all()

    ctx.push()

    yield testing_client  # this is where the testing happens!

    db.drop_all()
    ctx.pop()


@pytest.fixture(scope='module')
def init_database():
    # Create the database and the database table
    db.create_all()

    # Insert user data
    user1 = User(username='john', email='patkennedy79@gmail.com')
    user2 = User(username='kale', email='kennedyfamilyrecipes@gmail.com')
    db.session.add(user1)
    db.session.add(user2)

    # Commit the changes for the users
    db.session.commit()

    yield db  # this is where the testing happens!

    db.drop_all()


def test_home_page(client, init_database):
    response = client.get('/tips')
    assert response.status_code == 200


def test_notification_empty_list(client):
    response = client.get('/notifications')
    assert response.status_code == 200


def test_search_post(client):
    pass


def test_create_and_like_post(client):
    pass


def test_flash_messages(client):
    pass


def test_lang_change(client):
    pass
