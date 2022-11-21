import requests, json

XBOXLIVE_AUTH_URL = "https://user.auth.xboxlive.com/user/authenticate"
XSTS_AUTH_URL = "https://xsts.auth.xboxlive.com/xsts/authorize"

MC_AUTH_URL = "https://api.minecraftservices.com/authentication/login_with_xbox"
MC_PROFILE_URL = "https://api.minecraftservices.com/minecraft/profile"
MC_JOIN_URL = "https://sessionserver.mojang.com/session/minecraft/join"

def xboxlive_get_token_and_userhash(access_token):
    data = {
        "Properties":{
            "AuthMethod": "RPS",
            "SiteName": "user.auth.xboxlive.com",
            "RpsTicket": "d=" + access_token,
        },
        "RelyingParty": "http://auth.xboxlive.com",
        "TokenType": "JWT",
    }

    r = requests.post(XBOXLIVE_AUTH_URL, json=data)
    resp = json.loads(r.text)

    return resp["Token"], resp["DisplayClaims"]["xui"][0]["uhs"]

def xsts_get_token(xbl_token):
    data = {
        "Properties": {
            "SandboxId": "RETAIL",
            "UserTokens": [
                xbl_token
            ]
        },
        "RelyingParty": "rp://api.minecraftservices.com/",
        "TokenType": "JWT"
    }

    r = requests.post(XSTS_AUTH_URL, json=data)
    resp = json.loads(r.text)

    return resp["Token"]

def mc_auth_with_xbox(userhash, xsts_token):
    data = {"identityToken": "XBL3.0 x=" + userhash + ";" + xsts_token}
    r = requests.post(MC_AUTH_URL, json=data)
    resp = json.loads(r.text)

    return resp["access_token"]

def get_mc_token(oauth_token):
    xbl_token, userhash = xboxlive_get_token_and_userhash(oauth_token)
    xsts_token = xsts_get_token(xbl_token)
    mc_token = mc_auth_with_xbox(userhash, xsts_token)

    return mc_token

def get_mc_profile(mc_token):
    r = requests.get(MC_PROFILE_URL, headers={'Authorization': 'Bearer ' + mc_token})
    resp = json.loads(r.text)
    return resp["name"], resp["id"]

def auth_mc_join(mc_token, user_uuid, server_hash):
    data = {
        "accessToken": mc_token,
        "selectedProfile": user_uuid,
        "serverId": server_hash,
    }

    r = requests.post(MC_JOIN_URL, json=data)
    if r.status_code == 204:
        pass
    else:
        return json.loads(r.text)["error"]

