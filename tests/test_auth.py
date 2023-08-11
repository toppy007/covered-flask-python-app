import pytest
from flask import url_for

def test_login(client):
    response = client.post('/login', data={'email': 'testuser@example.com', 'password': 'testpassword'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Logged in successfully!' in response.data

def test_login_incorrect_password(client):
    response = client.post('/login', data={'email': 'testuser@example.com', 'password': 'wrongpassword'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Incorrect password, try again.' in response.data

def test_login_nonexistent_email(client):
    response = client.post('/login', data={'email': 'nonexistent@example.com', 'password': 'testpassword'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Email does not exist.' in response.data
