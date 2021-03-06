from pypresence import Presence
import time
import hashlib
import os
from rauth import OAuth2Service
from config import *


def get_noun(number, one, two, five):
    n = abs(number)
    n %= 100
    if 5 <= n <= 20:
      return five
    n %= 10
    if n == 1:
      return one
    if 2 <= n <= 4:
        return two
    return five


RPC = Presence(client_id)
RPC.connect()

service = OAuth2Service(
    client_id=waka_id,
    client_secret=waka_secret,
    name='wakatime',
    authorize_url='https://wakatime.com/oauth/authorize',
    access_token_url='https://wakatime.com/oauth/token',
    base_url='https://wakatime.com/api/v1/')

redirect_uri = 'https://wakatime.com/oauth/test'
state = hashlib.sha1(os.urandom(40)).hexdigest()
params = {'scope': 'email,read_stats',
          'response_type': 'code',
          'state': state,
          'redirect_uri': redirect_uri}

url = service.get_authorize_url(**params)

print('**** Visit this url in your browser ****'.format(url=url))
print('*' * 80)
print(url)
print('*' * 80)
print('**** After clicking Authorize, paste code here and press Enter ****')
code = input('Enter code from url: ')

headers = {'Accept': 'application/x-www-form-urlencoded'}
print('Getting an access token...')
session = service.get_auth_session(headers=headers,
                                   data={'code': code,
                                         'grant_type': 'authorization_code',
                                         'redirect_uri': redirect_uri})

print('Getting current user from API...')
user = session.get('users/current').json()
print('Authenticated via OAuth as {0}'.format(user['data']['email']))

while True:
    print("Getting user's coding stats from API...")
    stats = session.get('users/current/stats/last_7_days').json()

    hours = int(stats['data']['total_seconds'] // 3600)
    minutes = int(stats['data']['total_seconds'] // 60)
    state = f"{hours} {get_noun(hours, 'час', 'часа', 'часов')} {minutes} {get_noun(minutes, 'минута', 'минуты', 'минут')}\n\n"
    RPC.update(details=state, state='Данные обновляются каждый день', small_image='code')
    time.sleep(3600)
