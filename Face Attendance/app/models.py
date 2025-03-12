from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import numpy as np

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'admin' or 'student'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def is_admin(self):
        return self.role == 'admin'

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('student', uselist=False))
    face_encoding = db.Column(db.LargeBinary, nullable=True)
    
    def set_face_encoding(self, encoding):
        """Store face encoding as bytes"""
        if isinstance(encoding, np.ndarray):
            self.face_encoding = encoding.tobytes()
        else:
            self.face_encoding = encoding
            
    def get_face_encoding(self):
        """Get face encoding as numpy array"""
        return np.frombuffer(self.face_encoding, dtype=np.float64) if self.face_encoding else None
    
    def __repr__(self):
        return f'<Student {self.name}>'

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='present')
    
    student = db.relationship('Student', backref=db.backref('attendances', lazy=True))
    
    def __repr__(self):
        return f'<Attendance {self.student.name} - {self.timestamp}>'

    __table_args__ = (
        db.UniqueConstraint('student_id', 'timestamp', name='unique_student_timestamp'),
    )