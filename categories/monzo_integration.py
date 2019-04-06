from datetime import datetime, timedelta
from typing import Dict, List
from urllib.parse import urlencode, urlunsplit

from django.conf import settings
from django.core.exceptions import PermissionDenied

import requests

from .models import Transaction, MonzoUser
from mysite.settings import MONZO_CLIENT_ID, MONZO_CLIENT_SECRET

API_ROOT = 'https://api.monzo.com'
AUTH_ROOT = 'https://auth.monzo.com'
OAUTH_TOKEN_ENDPOINT = f'{API_ROOT}/oauth2/token'

# Improving this is out-of-scope for now
OAUTH_STATE_TOKEN = 'foobar'


class MonzoException(Exception):
    pass


# Does this make sense?
class NoAccessTokenException(MonzoException):
    pass


class MonzoAuth:
    WHOAMI_ENDPOINT = f'{API_ROOT}/ping/whoami'

    def __init__(self):
        # Read tokens saved in DB
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
        except PermissionDenied as e:
            print('refresh was NOT successful, need a redirect to the login page')
            raise NoAccessTokenException(e)

    @access_token.setter
    def access_token(self, value):
        self._access_token = value
        self._monzo_user.access_token = value
        self._monzo_user.save()

    @property
    def refresh_token(self):
        return self._refresh_token

    @refresh_token.setter
    def refresh_token(self, value):
        self._refresh_token = value
        self._monzo_user.refresh_token = value
        self._monzo_user.save()

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
        r = requests.post(OAUTH_TOKEN_ENDPOINT, data)
        data = r.json()

        if r.status_code == 200:
            self.access_token = data['access_token']
            self.refresh_token = data['refresh_token']

        elif data['code'] == 'unauthorized.bad_refresh_token.evicted':
            print('refresh_token has been evicted by another login')
            raise PermissionDenied(
                'refresh_token has been evicted by another login')

        elif data['code'] == 'unauthorized.bad_refresh_token':
            print('refresh_token is missing/malformed')
            raise PermissionDenied('refresh_token is missing/malformed')

        # what else could be done here?
        else:
            print(' unexpected error while refreshing tokens')
            raise Exception('unexpected error')


class MonzoRequest:
    TRANSACTIONS_ENDPOINT = f'{API_ROOT}/transactions'

    def __init__(self):
        # Catch user not in DB?
        monzo_user = MonzoUser.objects.all()[0]
        self.params = {'account_id': monzo_user.account_id}
        access_token = MonzoAuth().access_token
        # DRY
        self.headers = {'Authorization': f'Bearer {access_token}'}

    def get_days_of_spends(self, days: int = 7) -> List:
        some_days_ago = datetime.utcnow() - timedelta(days=days)
        since = some_days_ago.isoformat(timespec='seconds') + 'Z'
        params = {**self.params, 'since': since}

        r = requests.get(self.TRANSACTIONS_ENDPOINT,
                         params=params, headers=self.headers)
        data = r.json()

        transactions = data['transactions']
        spending = [t for t in transactions if t['include_in_spending']]
        return spending

    def get_transaction(self, id: str) -> Dict:
        params = {**self.params, 'expand[]': 'merchant'}
        url = f'{self.TRANSACTIONS_ENDPOINT}/{id}'
        r = requests.get(url, params=params, headers=self.headers)
        transaction = r.json()['transaction']
        return transaction

    def get_latest_transaction(self) -> Dict:
        spends = self.get_days_of_spends(days=7)
        latest_txid = spends[-1]['id']
        transaction = self.get_transaction(latest_txid)
        return transaction

    def get_latest_uningested_transaction(self) -> Dict:
        # this should paginate, would fix #6
        uningested = self.get_days_of_uningested_spends(days=30)
        latest_txid = uningested[-1]['id']
        transaction = self.get_transaction(latest_txid)
        return transaction

    def get_days_of_ingested_spends(self, days: int = 7) -> List:
        spends = self.get_days_of_spends(days=days)
        week_spend_ids = set([t['id'] for t in spends])
        # This model will need the Monzo created date saved to prevent slow queries
        all_ingested_ids = set(
            Transaction.objects.values_list('id', flat=True))

        week_ingested_ids = week_spend_ids.intersection(all_ingested_ids)
        week_ingested_monzo_transactions = [
            t for t in spends if t['id'] in week_ingested_ids]
        return week_ingested_monzo_transactions

    def get_days_of_uningested_spends(self, days: int = 7) -> List:
        spends = self.get_days_of_spends(days)
        week_spend_ids = set([t['id'] for t in spends])
        # This model will need the Monzo created date saved to prevent slow queries
        all_ingested_ids = set(
            Transaction.objects.values_list('id', flat=True))

        week_uningested_ids = week_spend_ids.difference(all_ingested_ids)
        week_uningested_monzo_transactions = [
            t for t in spends if t['id'] in week_uningested_ids]
        return week_uningested_monzo_transactions


def get_login_url(redirect_uri: str) -> str:
    client_id = MONZO_CLIENT_ID
    state_token = OAUTH_STATE_TOKEN

    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'state': state_token,
    }

    elements = ('https', 'auth.monzo.com', '', urlencode(params), '')
    url = urlunsplit(elements)

    return url


def exchange_authorization_code(authorization_code: str, redirect_uri: str) -> None:
    url = OAUTH_TOKEN_ENDPOINT
    client_id = MONZO_CLIENT_ID
    client_secret = MONZO_CLIENT_SECRET

    data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'code': authorization_code,
    }

    r = requests.post(url, data)
    data = r.json()

    if r.status_code != 200:
        raise Exception('Unexpected status code when exchanging oauth token')

    monzo_auth = MonzoAuth()
    monzo_auth.access_token = data['access_token']
    monzo_auth.refresh_token = data['refresh_token']
