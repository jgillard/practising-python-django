from datetime import datetime, timedelta
from typing import Dict, List

from django.conf import settings
from django.urls import reverse

import requests

from .models import TransactionData, MonzoUser


class MonzoRequest:
    monzo_api_root = 'https://api.monzo.com'
    whoami_endpoint = f'{monzo_api_root}/ping/whoami'
    refresh_endpoint = f'{monzo_api_root}/oauth2/token'
    transactions_endpoint = f'{monzo_api_root}/transactions'

    def __init__(self):
        self.monzo_user = MonzoUser.objects.all()[0]
        self.params = {'account_id': self.monzo_user.account_id}
        self.headers = {'Authorization': 'Bearer ' + self.monzo_user.access_token}

        # Firstly call Monzo /ping/whoami endpoint to check access_token state
        r = requests.get(self.whoami_endpoint, headers=self.headers)
        data = r.json()

        # It can be either invalid or expired, refresh on those situations
        if r.status_code != 200:
            if data['code'] == 'bad_request.invalid_token':
                print('access token has invalid, refreshing...')
                self.refresh_access_token()
        else:
            if data['authenticated'] is not True:
                print('access token has expired, refreshing...')
                self.refresh_access_token()
            else:
                print('access token is valid')

    def refresh_access_token(self) -> None:
        data = {
            'grant_type': 'refresh_token',
            'client_id': settings.MONZO_CLIENT_ID,
            'client_secret': settings.MONZO_CLIENT_SECRET,
            'refresh_token': self.monzo_user.refresh_token,
        }
        
        r = requests.post(self.refresh_endpoint, data)
        data = r.json()

        self.monzo_user.access_token = data['access_token']
        self.monzo_user.refresh_token = data['refresh_token']
        self.monzo_user.save()

        self.headers['Authorization'] = f'Bearer {self.monzo_user.access_token}'
        print('have refreshed user access & refresh tokens')

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
