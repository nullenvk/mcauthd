import requests
import json

REFRESH_URL = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"

def refresh_token(client_id, refresh_token):
    data = {"client_id": client_id,
            "scope": "XboxLive.signin offline_access",
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"}

    r = requests.post(REFRESH_URL, data=data)
    rdat = json.loads(r.text)

    return rdat["access_token"], rdat["refresh_token"], rdat["expires_in"]

class OAuthToken:
    def __init__(self, access_token, refresh_token):
        self.access_token = access_token
        self.refresh_token = refresh_token

    def refresh(self, client_id):
        self.access_token, self.refresh_token, ttl = refresh_token(client_id, self.refresh_token)
        return ttl
