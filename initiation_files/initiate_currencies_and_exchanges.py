import sys

if sys.platform == 'win32':
    sys.path.append("..")
else:
    sys.path.append(".")


import subprocess
import json
from financetracker import create_app
from financetracker.models import CurrencyUpdateStatus

command = 'curl "https://open.er-api.com/v6/latest/USD"'
result = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
result_json = json.loads(result.stdout.decode())

app = create_app()
with app.app_context():
    CurrencyUpdateStatus.update(result_json)


print('Initial Currency Insertion successful, please check tables "CurrencyUpdateStatus" and CurrencyExchanges')