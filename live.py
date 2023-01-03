import requests
import dotenv
import os
import time

dotenv.load_dotenv()


def get_twitch_oauth_token():
    # get oauth token using twitch api heli
    url = 'https://id.twitch.tv/oauth2/token'
    params = {
        'client_id': os.getenv('TWITCH_CLIENT_ID'),
        'client_secret': os.getenv('TWITCH_CLIENT_SECRET'),
        'grant_type': 'client_credentials',
    }

    r = requests.post(url, params=params)
    if r.status_code == 200:
        return r.json()['access_token']
    else:
        return None


def is_live(channel_name, secret):
    # check if live using twitch api heli
    url = f'https://api.twitch.tv/helix/streams?user_login={channel_name}'
    headers = {
        'Client-ID': os.getenv('TWITCH_CLIENT_ID'),
        'Authorization': f'Bearer { secret }'
    }

    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        if r.json()['data']:
            return True
        else:
            return False
    else:
        return False


def send_discord_webhook(channel_name):
    url = os.getenv('DISCORD_WEBHOOK_URL')

    # embed
    data = {
        'content': f'{channel_name} is live!',
        'embeds': [{
            'title': f'{channel_name} is live!',
            'url': f'https://twitch.tv/{channel_name}',
            'color': 0x6441A4,
            'thumbnail': {
                'url': f'https://static-cdn.jtvnw.net/previews-ttv/live_user_{channel_name}-320x180.jpg'
            }
        }]
    }

    r = requests.post(url, json=data)
    if r.status_code == 204:
        return True
    else:
        return False


oprint = print


def print(*args, **kwargs):
    oprint(f'[{time.strftime("%H:%M:%S")}]', *args, **kwargs)


if __name__ == '__main__':
    CHECK_DELAY = int(os.getenv('CHECK_DELAY'))
    CHANNEL_NAME = os.getenv('TWITCH_CHANNEL_NAME')
    SECRET = get_twitch_oauth_token()
    LIVE_SWITCH = False

    while True:
        if is_live(CHANNEL_NAME, SECRET):
            if not LIVE_SWITCH:
                print(f'{CHANNEL_NAME} is live! Sending webhook...')
                send_discord_webhook(CHANNEL_NAME)
                LIVE_SWITCH = True
            else:
                print(
                    f'{CHANNEL_NAME} is still live. Checking again in {CHECK_DELAY} seconds...')
        else:
            print(
                f'{CHANNEL_NAME} is not live. Checking again in {CHECK_DELAY} seconds...')
            if LIVE_SWITCH:
                LIVE_SWITCH = False

        time.sleep(CHECK_DELAY)
