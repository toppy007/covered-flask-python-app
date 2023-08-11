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

def test_logout(client):
    response = client.post('/login', data={'email': 'testuser@example.com', 'password': 'testpassword'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Logged in successfully!' in response.data

    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    with client.session_transaction() as session:
        assert 'user_id' not in session
        
    assert b'You have been logged out.' in response.data
    assert b'Login' in response.data 

def test_sign_up_existing_email(client):
    response = client.post('/sign-up', data={'email': 'testuser@example.com', 'firstName': 'Test', 'password1': 'testpassword', 'password2': 'testpassword'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Email already exists.' in response.data

def test_sign_up_short_email(client):
    response = client.post('/sign-up', data={'email': 'a@b', 'firstName': 'Test', 'password1': 'testpassword', 'password2': 'testpassword'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Email must be greater than 3 characters.' in response.data

def test_sign_up_short_first_name(client):
    response = client.post('/sign-up', data={'email': 'test@example.com', 'firstName': 'T', 'password1': 'testpassword', 'password2': 'testpassword'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'First name must be greater than 1 character.' in response.data

def test_sign_up_password_mismatch(client):
    response = client.post('/sign-up', data={'email': 'testnew@example.com', 'firstName': 'Test', 'password1': 'testpassword', 'password2': 'mismatchedpassword'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Passwords do not match.' in response.data

def test_sign_up_short_password(client):
    response = client.post('/sign-up', data={'email': 'test@example.com', 'firstName': 'Test', 'password1': 'short', 'password2': 'short'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Password must be at least 7 characters.' in response.data

def test_sign_up_success(client):
    response = client.post('/sign-up', data={'email': 'newuser@example.com', 'firstName': 'New', 'password1': 'strongpassword', 'password2': 'strongpassword'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Account created!' in response.data
    assert b'Profile' in response.data 
