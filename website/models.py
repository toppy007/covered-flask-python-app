from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_title = db.Column(db.String(10000))
    project_date = db.Column(db.String(10000))
    project_link = db.Column(db.String(10000))
    project_description = db.Column(db.String(10000))
    project_core_skill = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
class Workexp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workexp_title = db.Column(db.String(10000))
    workexp_company = db.Column(db.String(10000))
    workexp_dates = db.Column(db.String(10000))
    workexp_responsiblities = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(150))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
class OpenAiApiKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(150))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note', backref='user', lazy=True)
    skills = db.relationship('Skill', backref='user', lazy=True)
    api_keys = db.relationship('OpenAiApiKey', backref='user', lazy=True)
    projects = db.relationship('Project', backref='user', lazy=True)
    workexps = db.relationship('Workexp', backref='user', lazy=True)
    job_history_data = db.relationship('JobHistoryData', backref='user', lazy=True)
    
class JobHistoryData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sessions_data = db.Column(db.Text)
    covering_letter = db.Column(db.Text)
    job_ad = db.Column(db.Text)
    recruiters_name = db.Column(db.String(255))
    company_name = db.Column(db.String(255))
    ats_keywords = db.Column(db.Text)
    position = db.Column(db.String(255))
    technical_skills = db.Column(db.Text)
    rejested = db.Column(db.Integer, default=0)
    tech_interview = db.Column(db.Integer, default=0)
    contact_viewed = db.Column(db.Integer, default=0)
    interview = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))