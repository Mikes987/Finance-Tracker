import sqlalchemy as sa
import sqlalchemy.orm as so
from financetracker import db, login
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from flask import current_app
import jwt
from datetime import datetime, timedelta


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(32), unique=True, index=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(64), unique=True, index=True)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(256))
    
    def __repr__(self):
        return f'<User: "{self.username}">'
    
    @staticmethod
    def get_user(username: str, password: str):
        user = db.session.scalar(sa.select(User).where(User.username==username))
        if user:
            if check_password_hash(user.password_hash, password):
                return user
    
    @staticmethod
    def get_user_by_mail(email: str):
        return db.session.scalar(sa.select(User).where(User.email==email))
    
    @staticmethod
    def create_user(username:str, password: str, email:str):
        user = User(username=username, email=email)
        user.create_password(password)
        db.session.add(user)
        db.session.commit()
    
    def create_password(self, password: str):
        password_hash = generate_password_hash(password)
        self.password_hash = password_hash
    
    def request_password_token(self, duration=600):
        token = jwt.encode({'reset_password': self.id, 'exp': datetime.now() + timedelta(seconds=duration)},
                           current_app.config['SECRET_KEY'],
                           algorithm='HS256')
        return token
    
    @staticmethod
    def verify_token(token):
        user_id = jwt.decode(jwt=token, key=current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        user = db.session.get(User, user_id)
        return user
        


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))