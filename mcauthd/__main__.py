import argparse, sys, json, atexit
from pathlib import Path

from .authserver import AuthServer

def _save_db(authsrv, db_path):
    Path(db_path).write_text(json.dumps(authsrv.save_to_dict()))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            prog = "mcauthd",
            description = "Minecraft-compatible authentication daemon",
            epilog = "")

    parser.add_argument("bind_address", nargs = 1,
                        help = "Address on which the server's socket should get bind")

    parser.add_argument('-i', '--oauth-cid', dest = "oauth_cid", nargs = 1, required = False,
                        help = "Set the OAuth client ID")

    parser.add_argument('-d', '--db', dest = "db", nargs = 1, required = False,
                        help = "Provide the json file for storing active tokens")

    args = parser.parse_args()

    db_enabled = args.db != None 
    cid_enabled = args.oauth_cid != None 

    if not cid_enabled and not db_enabled: 
        print("ERROR: You must supply the OAuth client ID and/or the json file")
        parser.print_help()
        sys.exit(1)

    srv = AuthServer()
    
    if db_enabled: 
        p = Path(args.db[0])
        if p.is_file():
            srv.load_from_dict(json.loads(p.read_text()))
        else:
            p.write_text("")
        atexit.register(_save_db, srv, args.db[0])

    if cid_enabled:
        srv.oauth_cid = args.oauth_cid[0] 

    srv.run(args.bind_address[0])
