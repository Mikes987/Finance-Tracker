import sqlalchemy as sa
import sqlalchemy.orm as so
from financetracker import db, login
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from werkzeug.security import check_password_hash


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(32), unique=True, index=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(64), unique=True, index=True)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(256))
    
    @staticmethod
    def get_user(username: str, password: str):
        user = db.session.scalar(sa.select(User).where(User.username==username))
        if user:
            if check_password_hash(user.password_hash, password):
                return user
    
    def __repr__(self):
        return f'<User: "{self.username}">'


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))