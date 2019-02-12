from datetime import datetime, timedelta
from typing import Dict, List

import requests

from django.conf import settings

from .models import TransactionData


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

    def get_latest_transaction(self) -> Dict:
        spends = self.get_week_of_spends()
        latest_txid = spends[-1]['id']

        params = {**self.params, 'expand[]': 'merchant'}
        r = requests.get(f'{self.transactions_endpoint}/{latest_txid}', params=params, headers=self.headers)
        transaction = r.json()['transaction']
        return transaction

    def get_week_of_ingested_spends(self) -> List:
        spends = self.get_week_of_spends()
        spend_ids = set([t['id'] for t in spends])
        # This model will need the Monzo created date saved to prevent slow queries
        all_ingested_ids = set(TransactionData.objects.values_list('txid', flat=True))

        week_ingested_ids = spend_ids.intersection(all_ingested_ids)
        week_ingested_monzo_transactions = [t for t in spends if t['id'] in week_ingested_ids]
        return week_ingested_monzo_transactions

    def get_week_of_uningested_spends(self) -> List:
        spends = self.get_week_of_spends()
        spend_ids = set([t['id'] for t in spends])
        all_ingested_ids = set(TransactionData.objects.values_list('txid', flat=True))

        week_uningested_ids = spend_ids.difference(all_ingested_ids)
        week_uningested_monzo_transactions = [t for t in spends if t['id'] in week_uningested_ids]
        return week_uningested_monzo_transactions

    def get_latest_uningested_transaction(self) -> Dict:
        uningested = self.get_week_of_uningested_spends()
        latest_txid = uningested[-1]['id']

        params = {**self.params, 'expand[]': 'merchant'}
        r = requests.get(f'{self.transactions_endpoint}/{latest_txid}', params=params, headers=self.headers)
        transaction = r.json()['transaction']
        return transaction
