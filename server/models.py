from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates

from config import db, bcrypt


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    _password_hash = db.Column(db.String(128), nullable=False)

    notes = db.relationship('Note', back_populates='user', cascade='all, delete-orphan')

    # Ensure username is present and unique before saving
    @validates('username')
    def validate_username(self, key, value):
        if not value or not value.strip():
            raise ValueError("Username cannot be empty.")
        existing = User.query.filter_by(username=value.strip()).first()
        if existing and existing.id != self.id:
            raise ValueError("Username must be unique.")
        return value.strip()

    # Block direct reading of password_hash
    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hashes may not be viewed.")

    # Hash plain-text password with Bcrypt before storing in _password_hash
    @password_hash.setter
    def password_hash(self, password):
        if not password or len(password) < 4:
            raise ValueError("Password must be at least 4 characters long.")
        hashed = bcrypt.generate_password_hash(password.encode('utf-8'))
        self._password_hash = hashed.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8')
        )

    def __repr__(self):
        return f"<User {self.id}: {self.username}>"


class Note(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', back_populates='notes')

    @validates('title')
    def validate_title(self, key, value):
        if not value or not value.strip():
            raise ValueError("Note title is required.")
        return value.strip()

    @validates('content')
    def validate_content(self, key, value):
        if not value or not value.strip():
            raise ValueError("Note content is required.")
        return value.strip()

    def __repr__(self):
        return f"<Note {self.id}: {self.title}>"