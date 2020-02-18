import os

import pytest


from app import create_app, db
from app.models import User, Tip
from config import basedir


def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)


@pytest.fixture(scope='module')
def client():
    app = create_app()

    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    client = app.test_client()

    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('TEST_DATABASE_URL') \
                                            or 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()
    db.create_all()
    u = User(username='smith', email='smith@example.com', confirmed=True)
    u.set_password('1q2w3e')

    t = Tip(body='hello there', moderated=True, user_id=1)
    db.session.add(t)
    db.session.add(u)
    db.session.commit()

    yield client  # this is where the testing happens!
    db.session.remove()
    db.drop_all()
    os.remove(os.path.join(basedir, 'data-test.sqlite'))
    ctx.pop()


def test_home_page(client):
    response = client.get('/tips')
    assert b'hello there' in response.data
    assert response.status_code == 200


def test_login_logout(client):
    response = login(client, 'smith', '1q2w3e')
    assert response.status_code == 200


def test_create_post_no_user(client):
    response = client.post('/tips/new', data=dict(
        tip='new tip'
    ), follow_redirects=True)
    assert b'Please log in to access this page' in response.data


def test_create_post_with_user(client):
    login(client, 'smith', '1q2w3e')
    response = client.post('/tips/new', data=dict(
        tip='new tip',
        hashtags=''
    ), follow_redirects=True)
    assert b'Your tip is now live!' in response.data


def test_get_hashtags(client):
    response = client.get('/tips/hashtags')
    assert response.status_code == 200


def test_notification_empty_list(client):
    response = client.get('/notifications')
    assert response.status_code == 200


def test_search_post(client):
    response = client.get('/tips/search')
    assert b'hello there' in response.data


def test_create_and_like_post(client):
    pass


def test_flash_messages(client):
    pass


def test_lang_change(client):
    pass
