from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='student', nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    resume = db.Column(db.String(255), nullable=True)
    blacklisted = db.Column(db.Boolean, default=False)
    applications = db.relationship('Application', backref='student', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Student {self.name}>'

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    hr_contact = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    approved = db.Column(db.Boolean, default=False)
    blacklisted = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text, nullable=True)
    drives = db.relationship('Drive', backref='company', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Company {self.name}>'

class Drive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    eligibility = db.Column(db.String(255), nullable=True)
    deadline = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(30), default='Pending', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    applications = db.relationship('Application', backref='drive', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Drive {self.title} ({self.status})>'

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('drive.id'), nullable=False)
    applied_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(30), default='Applied', nullable=False)
    comments = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Application student={self.student_id} drive={self.drive_id} status={self.status}>'
