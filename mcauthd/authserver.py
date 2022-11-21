import time, zmq
from datetime import datetime, timedelta

from .oauth import OAuthToken
from .mc import get_mc_token, get_mc_profile, auth_mc_join

class UserData:
    def __init__(self, oauth_token, expire_date):
        self.oauth_token = oauth_token
        self.mc_token = ""
        self.expire_date = expire_date 
        self.username = ""

    def refresh_oauth(self, oauth_cid):
        ttl = self.oauth_token.refresh(oauth_cid)
        ttl = min(0, ttl - 1)
        self.expire_date = datetime.now() + timedelta(seconds=ttl)

    def refresh_mctoken(self):
        self.mc_token = get_mc_token(self.oauth_token.access_token)

    def refresh_profile(self):
        self.username, self.uuid = get_mc_profile(self.mc_token) 
        return self.username

    def refresh_all(self, oauth_cid):
        self.refresh_oauth(oauth_cid)
        self.refresh_mctoken()
        self.refresh_profile()

class AuthServer:
    def __init__(self):
        self.users = {}
        self.oauth_cid = ""

    def load_from_dict(self, du):
        self.oauth_cid = du["oauth_client_id"]

        for k in du["users"]:
            v = du["users"][k]

            dt = datetime.fromisoformat(v["expire_date"])
            obj = UserData(OAuthToken(v["oauth_token"], v["refresh_token"]), dt) 
            obj.username = k 
            self.users[k] = obj

    def save_to_dict(self):
        du = {}
        for k in self.users:
            v = self.users[k]
            dat = {
                "oauth_token": v.oauth_token.access_token,
                "refresh_token": v.oauth_token.refresh_token,
                "expire_date": v.expire_date.isoformat('T')
            }

            du[k] = dat

        return {"oauth_client_id": self.oauth_cid, "users": du}

    def create_user(self, access_token, refresh_token):
        try:
            u = UserData(OAuthToken(access_token, refresh_token), datetime.now())
            u.refresh_all(self.oauth_cid)
            self.users[u.username] = u

            print("Added user", u.username) 
            self.socket.send(b"OK")
        except Exception as e:
            print("User Creation Exception: ", e)
            self.socket.send(b"ERR")

    def auth_user(self, username):
        try:
            if not username in self.users:
                self.socket.send(b"NOACC")
                return

            u = self.users[username]
            oldname = u.username

            if u.expire_date < datetime.now():
                u.refresh_all(self.oauth_cid)
            else:
                u.refresh_mctoken()
                u.refresh_profile()

            del self.users[oldname]
            self.users[u.username] = u

            print("Authenticating", u.username)
            self.socket.send(b"OK " + bytes(u.username, 'ascii'))
                
        except Exception as e:
            print("Minecraft Auth Exception: ", e)
            self.socket.send(b"ERR")

    def join_user(self, username, server_hash):
        try:
            u = self.users[username]
            r = auth_mc_join(u.mc_token, u.uuid, server_hash)

            if r == None:
                self.socket.send(b"OK")
            elif r == "UserBannedException":
                self.socket.send(b"BAN")
            else:
                self.socket.send(b"ERR")

        except Exception as e:
            print("User join exception:", e)
            self.socket.send(b"ERR")

    def run(self, addr):
        zmq_ctx = zmq.Context()
        self.socket = zmq_ctx.socket(zmq.REP)
        self.socket.bind(addr)

        while True:
            rdat = self.socket.recv()
            req = str(rdat, encoding="ascii").split()

            if len(req) <= 0:
                self.socket.send(b"ERR")
                continue

            if req[0] == "ADD" and len(req) == 3:
                self.create_user(req[1], req[2])

            elif req[0] == "AUTH" and len(req) == 2:
                self.auth_user(req[1])

            elif req[0] == "JOIN" and len(req) == 3:
                self.join_user(req[1], req[2])

            else:
                self.socket.send(b"ERR")
