from website import create_app, db
from website.models import User, Note, Skill, OpenAiApiKey

def test_user_model(app):
    with app.app_context():
        user = User(email='test@example.com', password='password', first_name='Test')
        db.session.add(user)
        db.session.commit()

        queried_user = User.query.filter_by(email='test@example.com').first()
        assert queried_user is not None
        assert queried_user.first_name == 'Test'

def test_note_model(app):
    with app.app_context():
        user = User(email='test@example.com', password='password', first_name='Test')
        note = Note(data='Test note', user=user)
        db.session.add(user)
        db.session.add(note)
        db.session.commit()

        queried_note = Note.query.filter_by(data='Test note').first()
        assert queried_note is not None
        assert queried_note.user.first_name == 'Test'



