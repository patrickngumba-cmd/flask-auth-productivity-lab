import pytest
from app import app, db
from models import User, Note


@pytest.fixture
def client():
    app.config['TESTING'] = True

    with app.app_context():
        db.create_all()
        Note.query.delete()
        User.query.delete()
        db.session.commit()

        u1 = User(username="alice")
        u1.password_hash = "pass1234"
        u2 = User(username="bob")
        u2.password_hash = "pass5678"
        db.session.add_all([u1, u2])
        db.session.commit()

        for i in range(1, 7):
            db.session.add(Note(title=f"Alice Note {i}", content=f"Content {i}", user_id=u1.id))
        db.session.add(Note(title="Bob Secret Note", content="Bob only", user_id=u2.id))
        db.session.commit()

        with app.test_client() as client:
            yield client


def test_signup_and_check_session(client):
    res = client.post('/signup', json={"username": "charlie", "password": "mypassword"})
    assert res.status_code == 201
    data = res.get_json()
    assert data['username'] == "charlie"
    assert "_password_hash" not in data

    session_res = client.get('/check_session')
    assert session_res.status_code == 200
    assert session_res.get_json()['username'] == "charlie"


def test_login_and_logout(client):
    bad_res = client.post('/login', json={"username": "alice", "password": "wrong"})
    assert bad_res.status_code == 401

    login_res = client.post('/login', json={"username": "alice", "password": "pass1234"})
    assert login_res.status_code == 200

    logout_res = client.delete('/logout')
    assert logout_res.status_code == 204

    check_res = client.get('/check_session')
    assert check_res.status_code == 401


def test_unauthenticated_access_blocked(client):
    assert client.get('/notes').status_code == 401
    assert client.post('/notes', json={"title": "T", "content": "C"}).status_code == 401
    assert client.patch('/notes/1', json={"title": "Updated"}).status_code == 401
    assert client.delete('/notes/1').status_code == 401


def test_notes_pagination_and_ownership(client):
    client.post('/login', json={"username": "alice", "password": "pass1234"})

    page1 = client.get('/notes?page=1&per_page=4')
    assert page1.status_code == 200
    data1 = page1.get_json()
    assert len(data1['notes']) == 4
    assert data1['total'] == 6
    assert data1['total_pages'] == 2

    page2 = client.get('/notes?page=2&per_page=4')
    data2 = page2.get_json()
    assert len(data2['notes']) == 2


def test_user_cannot_modify_other_users_notes(client):
    client.post('/login', json={"username": "alice", "password": "pass1234"})

    patch_res = client.patch('/notes/7', json={"title": "Hacked"})
    assert patch_res.status_code == 404

    del_res = client.delete('/notes/7')
    assert del_res.status_code == 404


def test_create_update_and_delete_own_note(client):
    client.post('/login', json={"username": "bob", "password": "pass5678"})

    create_res = client.post('/notes', json={"title": "New Task", "content": "Finish report"})
    assert create_res.status_code == 201
    note_id = create_res.get_json()['id']

    patch_res = client.patch(f'/notes/{note_id}', json={"title": "Updated Task"})
    assert patch_res.status_code == 200
    assert patch_res.get_json()['title'] == "Updated Task"

    del_res = client.delete(f'/notes/{note_id}')
    assert del_res.status_code == 200
