# mcauthd - Minecraft session/token tracking daemon

## How to run it?
First run: `python3 -m mcauthd -d db_file.json -i OAUTH_CLIENT_ID tcp://*:5555`
Normal run: `python3 -m mcauthd -d db_file.json tcp://*:5555`

## RPC

You can interact with the server over by connecting with a ZeroMQ request socket and using these commands:

- ADD <accessToken> <refreshToken>: Add a new account by importing its OAuth tokens. Requires `XboxLive.signin` and `offline_access` in login request's scope parameter.
    Reply: OK / ERR

- AUTH <nickname>: Try to authenticate using existing account, refreshing all tokens beforehand (to ensure that the client can spend as much time being connected to the game server as possible).
    Reply: OK <new_nickname> / NOACC / ERR
    
    NOACC - No account found bearing that nickname

- JOIN <nickname> <serverHash>: Authenticate a Minecraft client joining an online server, doesn't refresh any tokens
    Reply: OK / BAN / ERR
