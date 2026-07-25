"""Finish Etsy OAuth: exchange code from redirect URL for tokens."""
import json
import sys
import urllib.parse

import auth

if len(sys.argv) < 2:
    print('Usage: py -3.11 _oauth_finish.py "https://mathrelaxing.store/callback?code=...&state=..."')
    sys.exit(1)

redirected = sys.argv[1].strip().strip('"').strip("'")
pending = json.load(open("_oauth_pending.json", encoding="utf-8"))
params = urllib.parse.parse_qs(urllib.parse.urlparse(redirected).query)
if "code" not in params:
    print("No 'code' in URL. Copy the full redirect URL including ?code=...")
    sys.exit(1)
code = params["code"][0]
auth.exchange_code_for_token(code, pending["code_verifier"])
print("Reauth complete. Token in etsy_token.json")
print("Verify with: py -3.11 _check_etsy_api.py")
