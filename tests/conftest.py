import pytest

from website.models import User, Note, Skill, OpenAiApiKey
from website import create_app, db, create_database
from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    app = create_app(testing=True)
    with app.app_context():
        create_database(app, testing=True)
        user = User(email='testuser@example.com', first_name='Test', password=generate_password_hash(
                "testpassword", method='sha256'))
        db.session.add(user)
        db.session.commit()
        yield app
        db.drop_all() 

@pytest.fixture
def client(app):
    return app.test_client()
