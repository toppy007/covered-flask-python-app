import pytest

from website import create_app, db, create_database

@pytest.fixture
def app():
    app = create_app(testing=True)
    with app.app_context():
        create_database(app, testing=True)  # Create test database
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()
