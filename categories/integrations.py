from datetime import datetime, timedelta
from typing import Dict, List

import requests

from django.conf import settings


class MonzoRequest:
    def __init__(self):
        self.transactions_endpoint = 'https://api.monzo.com/transactions'
        self.params = {'account_id': settings.MONZO_ACCOUNT_ID}
        self.headers = {'Authorization': 'Bearer ' + settings.MONZO_BEARER}

    def get_week_of_spends(self) -> List:
        one_week_ago = datetime.utcnow() - timedelta(days=7)
        since = one_week_ago.isoformat(timespec='seconds') + 'Z'
        params = {**self.params, 'since': since}

        r = requests.get(self.transactions_endpoint, params=params, headers=self.headers)

        data = r.json()
        spending = [t for t in data['transactions'] if t['include_in_spending']]

        return spending

    def get_transaction(self, id: str) -> Dict:
        params = {**self.params, 'expand[]': 'merchant'}

        r = requests.get(f'{self.transactions_endpoint}/{id}', params=params, headers=self.headers)

        transaction = r.json()['transaction']

        return transaction
