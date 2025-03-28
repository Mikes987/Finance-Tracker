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
    
    user_categories: so.WriteOnlyMapped['Category'] = so.relationship(back_populates='user')
    
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


class MainTypes(db.Model):
    __tablename__ = 'maintypes'
    
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    type: so.Mapped[str] = so.mapped_column(sa.String(32), unique=True)
    
    categories: so.WriteOnlyMapped['Category'] = so.relationship(back_populates='main_type')
    
    def __repr__(self):
        return f"<Type: {self.type}>"


class Category(db.Model):
    __tablename__ = 'categories'
    
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    category: so.Mapped[str] = so.mapped_column(sa.String(64), unique=True, index=True)
    main_type_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('maintypes.id'))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('users.id'))
    
    main_type: so.Mapped['MainTypes'] = so.relationship(back_populates='categories')
    user: so.Mapped['User'] = so.relationship(back_populates='user_categories')
    
    def __repr__(self):
        return f'<Category: "{self.category}">'


class CurrencyExchanges(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    exchange_value: so.Mapped[float]
    currency_to_dollar: so.Mapped[str] = so.mapped_column(sa.String(3))
    
    def __repr__(self):
        return f"<Currency Exchange_to_Dollar ({self.currency_to_dollar}: {self.exchange_value})"
    
    @staticmethod
    def update_exchange_rates(content: dict):
        keys = content.keys()
        for key in keys:
            exchange_rate = db.session.scalar(sa.select(CurrencyExchanges).where(CurrencyExchanges.currency_to_dollar==key))
            if exchange_rate == None:
                print("Creating new value for currency " + key)
                exchange_rate = CurrencyExchanges(currency_to_dollar=key)
            exchange_rate.exchange_value = content[key]
            db.session.add(exchange_rate)
        db.session.commit()


class  CurrencyUpdateStatus(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    last_update_unix: so.Mapped[int]
    last_update_string: so.Mapped[str] = so.mapped_column(sa.String(24))
    next_update_unix: so.Mapped[int]
    next_update_string: so.Mapped[str] = so.mapped_column(sa.String(24))
    
    def __repr__(self):
        return f'<CurrencyUpdateStatus (last update: {self.last_update_string})>'
    
    @staticmethod
    def update(content):
        if content['result'] != 'success':
            print("Load from API not successful")
        else:
            last_status = db.session.scalar(sa.select(CurrencyUpdateStatus).where(CurrencyUpdateStatus.id==1))
            if last_status == None:
                print("Creating initial status object")
                last_status = CurrencyUpdateStatus()
            else:
                if last_status.last_update_unix >= content['time_last_update_unix']:
                    print("No updates yet")
                    return
            print("Updates available")
            last_update = content['time_last_update_unix']
            last_update_string = datetime.strftime((datetime.fromtimestamp(last_update)), format='%y-%m-%d %H:%M:%S')
            next_update = content['time_next_update_unix']
            next_update_string = datetime.strftime((datetime.fromtimestamp(next_update)), format='%y-%m-%d %H:%M:%S')
            last_status.last_update_unix = last_update
            last_status.last_update_string = last_update_string
            last_status.next_update_unix = next_update
            last_status.next_update_string = next_update_string
            db.session.add(last_status)
            print("Adding currency exchanges")
            CurrencyExchanges.update_exchange_rates(content['rates'])
            