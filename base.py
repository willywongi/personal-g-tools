from urllib.parse import urlencode

import requests


class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def get_access_token(program, client_id, secret, scopes):
    access_token = None
    try:
        with open(f"{program}.auth_code") as handler:
            auth_code = handler.read()
    except IOError:
        auth_code = None

    if not auth_code:
        url = "https://accounts.google.com/o/oauth2/v2/auth?{}".format(urlencode({
                'scope': " ".join(scopes),
                'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
                'response_type': 'code',
                'client_id': client_id
            }, doseq=True))
        print(f"{BColors.BOLD}Visita il seguente indirizzo.{BColors.ENDC}")
        print(url)
        auth_code = input("Inserisci l'auth code: ")
        with open(f"{program}.auth_code", "w") as handler:
            handler.write(auth_code)

    try:
        with open(f"{program}.refresh_token") as handler:
            refresh_token = handler.read()
    except IOError:
        refresh_token = None

    if not refresh_token:
        response = requests.post("https://oauth2.googleapis.com/token", data={
                    'client_id': client_id,
                    'client_secret': secret,
                    'code': auth_code,
                    'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
                    'grant_type': 'authorization_code'
                })
        try:
            response.raise_for_status()
        except Exception:
            print(response.text)
            raise
        result = response.json()
        refresh_token = result["refresh_token"]
        access_token = result["access_token"]
        with open(f"{program}.refresh_token", "w") as handler:
            handler.write(result["refresh_token"])

    if not access_token:
        response = requests.post("https://oauth2.googleapis.com/token", data={
                    'client_id': client_id,
                    'client_secret': secret,
                    'refresh_token': refresh_token,
                    'grant_type': 'refresh_token'
                })
        try:
            response.raise_for_status()
        except Exception:
            print(response.text)
            raise
        result = response.json()
        access_token = result["access_token"]
    
    return access_token
