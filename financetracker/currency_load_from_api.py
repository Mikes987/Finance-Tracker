import json, subprocess

def load_currency_exchange_rates():
    command = 'curl "https://open.er-api.com/v6/latest/USD"'
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
    result_json = json.loads(result.stdout.decode())
    return result_json