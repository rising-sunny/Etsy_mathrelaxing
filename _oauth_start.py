"""Start Etsy OAuth reauth with full scopes (incl. transactions_r)."""
import json
import webbrowser

import auth

v, c = auth.generate_pkce_pair()
url, state = auth.get_authorization_url(c)
with open("_oauth_pending.json", "w", encoding="utf-8") as f:
    json.dump({"code_verifier": v, "state": state}, f)
print("SCOPES:", auth.SCOPES)
print()
print("1) Open this URL (login as shop owner + Accept):")
print()
print(url)
print()
print("2) After redirect, copy the FULL browser URL and run:")
print('   py -3.11 _oauth_finish.py "PASTE_URL_HERE"')
print()
try:
    webbrowser.open(url)
except Exception:
    pass
