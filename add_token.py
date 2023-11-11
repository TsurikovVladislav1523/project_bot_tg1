import requests
def add_token(code):
    token_data = {
                'grant_type': 'authorization_code',
                'code': code,
                'client_id': "561fc59ae9284fbeb00a15622c6d7d53",
                'client_secret': "ca91dbecef984d878946ed68eb16acf0"
            }
    URL = f"https://oauth.yandex.ru/token"
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'}
    r = requests.post(URL, headers=headers, data=token_data)
    return r.json()["access_token"]
