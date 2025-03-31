import sys

if sys.platform == 'win32':
    sys.path.append("..")
else:
    sys.path.append(".")

# import os

sys.path.append(".")
#content = os.listdir(sys.path[-1])


from financetracker import create_app, db
from financetracker.models import MainTypes
import sqlalchemy as sa

types = [
    {'id': 1, 'type': 'Income'},
    {'id': 2, 'type': 'Expenses'},
    {'id': 3, 'type': 'Savings'}
]

app = create_app()

with app.app_context():
    for t in types:
        mt = MainTypes(id=t['id'], type=t['type'])
        db.session.add(mt)
    db.session.commit()


print('Insertion successful, check table "Maintypes"')