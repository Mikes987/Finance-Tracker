import pandas as pd
import sqlalchemy as sa
import sqlalchemy.orm as so
from financetracker import db, login
from financetracker.currency_load_from_api import load_currency_exchange_rates
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask import current_app
import jwt
from datetime import datetime, timedelta, date
from decimal import Decimal


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(32), unique=True, index=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(64), unique=True, index=True)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(256))
    
    user_categories: so.WriteOnlyMapped['Category'] = so.relationship(back_populates='user')
    user_views: so.WriteOnlyMapped['View'] = so.relationship(back_populates='user')
    user_trackings: so.WriteOnlyMapped['Tracking'] = so.relationship(back_populates='tracking_user')
    
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
    
    def get_my_tracking_data(self):
        results = Tracking.get_all_tracking_data_by_user_and_view(self.id)
        return results
    
    def get_my_current_view(self):
        return View.get_current_view()
        


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class MainTypes(db.Model):
    __tablename__ = 'maintypes'
    
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    type: so.Mapped[str] = so.mapped_column(sa.String(32), unique=True)
    
    categories: so.WriteOnlyMapped['Category'] = so.relationship(back_populates='main_type')
    tracking: so.WriteOnlyMapped['Tracking'] = so.relationship(back_populates='main_type')
    
    def __repr__(self):
        return f"<Type: {self.type}>"
    
    @staticmethod
    def get_all_types():
        return db.session.scalars(sa.select(MainTypes.type).order_by(MainTypes.id)).all()
    
    @staticmethod
    def add_main_types():
        types = [
            {'id': 1, 'type': 'Income'},
            {'id': 2, 'type': 'Expenses'},
            {'id': 3, 'type': 'Savings'}
        ]
        for t in types:
            mt = MainTypes(id=t['id'], type=t['type'])
            db.session.add(mt)
            db.session.commit()
        print("Main Types added")
    
    @staticmethod
    def check_for_initial_types():
        if sum(MainTypes.get_all_types()) == 0:
            print("Adding Main Types")
            MainTypes.add_main_types()


class Category(db.Model):
    __tablename__ = 'categories'
    
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    category: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    main_type_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('maintypes.id'))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('users.id'))
    view_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('views.id'))
    
    main_type: so.Mapped['MainTypes'] = so.relationship(back_populates='categories')
    user: so.Mapped['User'] = so.relationship(back_populates='user_categories')
    view: so.Mapped['View'] = so.relationship(back_populates='categories')
    tracking_category: so.WriteOnlyMapped['Tracking'] = so.relationship(back_populates='category_tracking')
    
    def __repr__(self):
        return f'<Category: "{self.category}">'
    
    @staticmethod
    def create_category(main_type_string, category, view_id):
        main_type = db.session.scalar(sa.select(MainTypes).where(MainTypes.type==main_type_string))
        new_category = Category(category=category, main_type=main_type, user=current_user, view_id=int(view_id))
        db.session.add(new_category)
        db.session.commit()
    
    @staticmethod
    def get_all_categories(view_id):
        income_categories = db.session.scalars(sa.select(Category.category).where(Category.main_type_id==1, Category.user==current_user, Category.view_id==view_id).order_by(Category.category)).all()
        expense_categories = db.session.scalars(sa.select(Category.category).where(Category.main_type_id==2, Category.user==current_user, Category.view_id==view_id).order_by(Category.category)).all()
        savings_categories = db.session.scalars(sa.select(Category.category).where(Category.main_type_id==3, Category.user==current_user, Category.view_id==view_id).order_by(Category.category)).all()
        return income_categories, expense_categories, savings_categories


class CurrencyExchanges(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    exchange_value: so.Mapped[float]
    currency_to_dollar: so.Mapped[str] = so.mapped_column(sa.String(3))
    
    view: so.Mapped['View'] = so.relationship(back_populates='currency')
    
    def __repr__(self):
        return f"<Currency Exchange_to_Dollar ({self.currency_to_dollar}: {self.exchange_value})"
    
    @staticmethod
    def get_all_currencies():
        query = sa.select(CurrencyExchanges.currency_to_dollar).order_by(CurrencyExchanges.currency_to_dollar)
        result = db.session.scalars(query).all()
        return result
    
    @staticmethod
    def get_currency_by_string(currency_string: str):
        query = sa.select(CurrencyExchanges).where(CurrencyExchanges.currency_to_dollar==currency_string)
        result = db.session.scalar(query)
        return result
    
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
    
    @staticmethod
    def get_current_currency():
        current_currency_id = View.get_current_currency()
        query = sa.select(CurrencyExchanges.currency_to_dollar).where(CurrencyExchanges.id==current_currency_id)
        result = db.session.scalar(query)
        return result
    
    @staticmethod
    def get_currency_code_by_id(view_id):
        currency_id = View.get_currency_by_id(view_id)
        query = sa.select(CurrencyExchanges.currency_to_dollar).where(CurrencyExchanges.id==currency_id)
        currency_code = db.session.scalar(query)
        return currency_code
    
    @staticmethod
    def get_exchange_rate_by_currency_code(curr_code):
        query = sa.select(CurrencyExchanges.exchange_value).where(CurrencyExchanges.currency_to_dollar==curr_code)
        result = db.session.scalar(query)
        return result


class  CurrencyUpdateStatus(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    last_update_unix: so.Mapped[int]
    last_update_string: so.Mapped[str] = so.mapped_column(sa.String(24))
    next_update_unix: so.Mapped[int]
    next_update_string: so.Mapped[str] = so.mapped_column(sa.String(24))
    
    def __repr__(self):
        return f'<CurrencyUpdateStatus (last update: {self.last_update_string})>'
    
    @staticmethod
    def update_currency_exchanges():
        content = load_currency_exchange_rates()
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


class View(db.Model):
    __tablename__ = "views"
    
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('users.id'))
    currency_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('currency_exchanges.id'))
    is_active: so.Mapped[bool]
    
    user: so.Mapped['User'] = so.relationship(back_populates='user_views')
    categories: so.WriteOnlyMapped['Category'] = so.relationship(back_populates='view')
    currency: so.Mapped['CurrencyExchanges'] = so.relationship(back_populates='view')
    view_trackings: so.WriteOnlyMapped['Tracking'] = so.relationship(back_populates='tracking_view')
    
    def __repr__(self):
        return f"<View: {self.id}>"
    
    @staticmethod
    def get_number_of_views(userid):
        query = sa.select(sa.func.count(View.id)).where(View.user_id==userid)
        result = db.session.scalar(query)
        return result
    
    @staticmethod
    def get_current_view():
        query = sa.Select(View.id).where(View.user==current_user, View.is_active==True)
        result = db.session.scalar(query)
        return result
    
    @staticmethod
    def get_views_in_table(userid):
        query = sa.select(View.id, CurrencyExchanges.currency_to_dollar, View.is_active).join(CurrencyExchanges).where(View.user_id==userid)
        result = db.session.execute(query).all()
        return result
    
    @staticmethod
    def get_all_views_by_user():
        return db.session.scalars(sa.select(View).where(View.user==current_user)).all()
    
    @staticmethod
    def create_view(currency_string):
        currency = CurrencyExchanges.get_currency_by_string(currency_string)
        current_views = View.get_all_views_by_user()
        for view in current_views:
            view.is_active = False
        new_view = View(user=current_user, currency=currency, is_active=True)
        db.session.add(new_view)
        db.session.commit()
    
    @staticmethod
    def change_view(desired_view_id):
        current_views = View.get_all_views_by_user()
        for view in current_views:
            view.is_active = True if view.id == desired_view_id else False
        db.session.commit()
    
    @staticmethod
    def get_current_currency():
        current_view = View.get_current_view()
        query = sa.select(View.currency_id).where(View.id==current_view)
        currency_id = db.session.scalar(query)
        return currency_id
    
    @staticmethod
    def get_currency_by_id(view_id):
        query = sa.select(View.currency_id).where(View.id==int(view_id))
        currency_id = db.session.scalar(query)
        return currency_id


class Tracking(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    date: so.Mapped[date]
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('users.id'))
    view_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('views.id'))
    type_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('maintypes.id'))
    category_id: so.Mapped[int]
    # amount: so.Mapped[float]
    amount: so.Mapped[Decimal] = so.mapped_column(sa.types.DECIMAL(precision=2))
    source_target_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('categories.id'))
    comment: so.Mapped[str] = so.mapped_column(sa.String(96))
    
    main_type: so.Mapped['MainTypes'] = so.relationship(back_populates='tracking')
    category_tracking: so.Mapped['Category'] = so.relationship(back_populates='tracking_category')
    tracking_user: so.Mapped['User'] = so.relationship(back_populates='user_trackings')
    tracking_view: so.Mapped['View'] = so.relationship(back_populates='view_trackings')
    
    @staticmethod
    def create_tracking(entry_date, maintype, category, target_source, amount, comment):
        main_type = db.session.scalar(sa.select(MainTypes).where(MainTypes.type==maintype))
        category = db.session.scalar(sa.select(Category).where(Category.category==category, Category.main_type==main_type, Category.user==current_user))
        target = db.session.scalar(sa.select(Category).where(Category.category==target_source, Category.main_type_id==3, Category.user==current_user))
        view = View.get_current_view()
        new_tracking = Tracking(date=entry_date, tracking_user=current_user, view_id=view, category_id=category.id, main_type=main_type, amount=amount, category_tracking=target, comment=comment)
        db.session.add(new_tracking)
        db.session.commit()
    
    @staticmethod
    def get_all_tracking_data_by_user_and_view(userid):
        aliased_target = so.aliased(Category)
        # query = sa.select(Tracking.date, MainTypes.type, Category.category, Tracking.amount, aliased_target.category, Tracking.comment).select_from(Tracking).join(MainTypes).join(Category, Category.id==Tracking.category_id).join(aliased_target, aliased_target.id==Tracking.source_target_id).order_by(Tracking.date.desc(), Tracking.id.desc())
        query2 = query2 = sa.select(Tracking.id, Tracking.date, MainTypes.type, aliased_target.category, Tracking.amount, Category.category.label("Source/Target"), Tracking.comment, Tracking.view_id)\
            .select_from(Tracking)\
            .join(MainTypes)\
            .join(aliased_target, onclause=aliased_target.id==Tracking.category_id)\
            .join(Category, onclause=Tracking.source_target_id==Category.id)\
            .where(Tracking.user_id==userid)\
            .order_by(Tracking.date, Tracking.id)
        result = pd.read_sql(sql=query2, con=db.engine)
        return result
    
    @staticmethod
    def delete_tracking_entry(tracking_id: int):
        query = sa.delete(Tracking).where(Tracking.id==tracking_id)
        db.session.execute(query)
        db.session.commit()
        