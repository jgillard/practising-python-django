from datetime import datetime, timedelta
from typing import Dict, List

from django.conf import settings
from django.core.exceptions import PermissionDenied

import requests

from .models import TransactionData, MonzoUser


# Does this make sense?
class NoAccessTokenException(Exception):
    pass


class MonzoAuth:
    API_ROOT = 'https://api.monzo.com'
    WHOAMI_ENDPOINT = f'{API_ROOT}/ping/whoami'
    REFRESH_ENDPOINT = f'{API_ROOT}/oauth2/token'

    def __init__(self):
        # Read tokens saved in DB
        # Catch user not in DB?
        self._monzo_user = MonzoUser.objects.all()[0]
        self._access_token = self._monzo_user.access_token
        self._refresh_token = self._monzo_user.refresh_token

    @property
    def access_token(self):
        if self.access_token_valid():
            print('access_token is valid')
            return self._access_token

        try:
            print('access_token NOT valid, attempting refresh')
            self.use_refresh_token()
            print('refresh was successful')
            return self._access_token
        # this likely isn't best practice
        except PermissionDenied as e:
            print('refresh was NOT successful, need a redirect to the login page')
            print(e)
            # Should this happen?
            raise NoAccessTokenException()

    def access_token_valid(self) -> bool:
        # Call Monzo's whoami endpoint to determine token state
        headers = {'Authorization': f'Bearer {self._access_token}'}
        r = requests.get(self.WHOAMI_ENDPOINT, headers=headers)
        data = r.json()

        if r.status_code == 200 and data['authenticated'] is True:
            print('access_token is authenticated')
            return True

        if r.status_code == 200 and data['authenticated'] is not True:
            print('access_token is NOT authenticated')
            return False

        if r.status_code != 200:
            print('access_token whoami returned !200')
            return False

    def use_refresh_token(self) -> None:
        data = {
            'grant_type': 'refresh_token',
            'client_id': settings.MONZO_CLIENT_ID,
            'client_secret': settings.MONZO_CLIENT_SECRET,
            'refresh_token': self._refresh_token,
        }
        r = requests.post(self.REFRESH_ENDPOINT, data)
        data = r.json()

        if r.status_code == 200:
            # Likely should not be keeping these in memory
            # Will depend how the class is used
            self._access_token = data['access_token']
            self._refresh_token = data['refresh_token']

            self._monzo_user.access_token = data['access_token']
            self._monzo_user.refresh_token = data['refresh_token']
            self._monzo_user.save()

        elif data['code'] == 'unauthorized.bad_refresh_token.evicted':
            print('refresh_token has been evicted by another login')
            raise PermissionDenied('refresh_token has been evicted by another login')

        elif data['code'] == 'unauthorized.bad_refresh_token':
            print('refresh_token is missing/malformed')
            raise PermissionDenied('refresh_token is missing/malformed')

        # what else could be done here?
        else:
            print(' unexpected error while refreshing tokens')
            raise Exception('unexpected error')


class MonzoRequest:
    # DRY
    API_ROOT = 'https://api.monzo.com'
    TRANSACTIONS_ENDPOINT = f'{API_ROOT}/transactions'

    def __init__(self):
        # Catch user not in DB?
        monzo_user = MonzoUser.objects.all()[0]
        self.params = {'account_id': monzo_user.account_id}
        access_token = MonzoAuth().access_token
        # DRY
        self.headers = {'Authorization': f'Bearer {access_token}'}

    def get_week_of_spends(self) -> List:
        one_week_ago = datetime.utcnow() - timedelta(days=7)
        since = one_week_ago.isoformat(timespec='seconds') + 'Z'
        params = {**self.params, 'since': since}

        r = requests.get(self.TRANSACTIONS_ENDPOINT, params=params, headers=self.headers)
        data = r.json()

        spending = [t for t in data['transactions'] if t['include_in_spending']]
        return spending

    def get_transaction(self, id: str) -> Dict:
        params = {**self.params, 'expand[]': 'merchant'}
        r = requests.get(f'{self.TRANSACTIONS_ENDPOINT}/{id}', params=params, headers=self.headers)
        transaction = r.json()['transaction']
        return transaction

    def get_latest_transaction(self) -> Dict:
        spends = self.get_week_of_spends()
        latest_txid = spends[-1]['id']
        transaction = self.get_transaction(latest_txid)
        return transaction

    def get_latest_uningested_transaction(self) -> Dict:
        uningested = self.get_week_of_uningested_spends()
        latest_txid = uningested[-1]['id']
        transaction = self.get_transaction(latest_txid)
        return transaction

    def get_week_of_ingested_spends(self) -> List:
        spends = self.get_week_of_spends()
        week_spend_ids = set([t['id'] for t in spends])
        # This model will need the Monzo created date saved to prevent slow queries
        all_ingested_ids = set(TransactionData.objects.values_list('txid', flat=True))

        week_ingested_ids = week_spend_ids.intersection(all_ingested_ids)
        week_ingested_monzo_transactions = [t for t in spends if t['id'] in week_ingested_ids]
        return week_ingested_monzo_transactions

    def get_week_of_uningested_spends(self) -> List:
        spends = self.get_week_of_spends()
        week_spend_ids = set([t['id'] for t in spends])
        # This model will need the Monzo created date saved to prevent slow queries
        all_ingested_ids = set(TransactionData.objects.values_list('txid', flat=True))

        week_uningested_ids = week_spend_ids.difference(all_ingested_ids)
        week_uningested_monzo_transactions = [t for t in spends if t['id'] in week_uningested_ids]
        return week_uningested_monzo_transactions
