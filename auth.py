import base64
import hashlib
import secrets
import urllib.parse
import urllib.request
import webbrowser
import json
import os

CLIENT_ID = "1nkkipgbsfholyrhfkqqqkjj"
# Scopes necesarios para administrar listings
SCOPES = "listings_r listings_w shops_r"
REDIRECT_URI = "https://mathrelaxing.store/callback"
TOKEN_FILE = "etsy_token.json"

def generate_pkce_pair():
    # Genera un code_verifier y code_challenge para OAuth 2.0 PKCE
    code_verifier = secrets.token_urlsafe(32)
    code_challenge = hashlib.sha256(code_verifier.encode('ascii')).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode('ascii').rstrip('=')
    return code_verifier, code_challenge

def get_authorization_url(code_challenge):
    state = secrets.token_urlsafe(16)
    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPES,
        'state': state,
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256'
    }
    url = "https://www.etsy.com/oauth/connect?" + urllib.parse.urlencode(params)
    return url, state

def exchange_code_for_token(code, code_verifier):
    url = "https://api.etsy.com/v3/public/oauth/token"
    data = urllib.parse.urlencode({
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'code': code,
        'code_verifier': code_verifier
    }).encode('ascii')
    
    req = urllib.request.Request(url, data=data)
    
    print("\nSolicitando token a Etsy...")
    try:
        with urllib.request.urlopen(req) as response:
            token_data = json.loads(response.read().decode('utf-8'))
            with open(TOKEN_FILE, 'w') as f:
                json.dump(token_data, f)
            print(f"\n¡Éxito! Token guardado en {TOKEN_FILE}.")
            return token_data
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(e, 'read'):
            print(e.read().decode('utf-8'))

def main():
    print("=== Autenticación de Etsy API v3 ===")
    
    # 1. Generar PKCE
    code_verifier, code_challenge = generate_pkce_pair()
    
    # 2. Generar URL
    auth_url, state = get_authorization_url(code_challenge)
    
    print("\n[URL DE AUTORIZACION]")
    print(auth_url)
    print("[/URL DE AUTORIZACION]")
    
    # Intenta abrir el navegador automáticamente
    try:
        webbrowser.open(auth_url)
    except:
        pass
        
    print("\nCopia la URL completa de la barra de direcciones de tu navegador y pégala aquí.")
    
    # 3. Leer URL redirigida
    redirected_url = input("\nPega la URL completa aquí: ").strip()
    
    # Extraer el 'code' de la URL
    try:
        parsed_url = urllib.parse.urlparse(redirected_url)
        params = urllib.parse.parse_qs(parsed_url.query)
        code = params['code'][0]
    except KeyError:
        print("\nError: No se encontró el 'code' en la URL. Asegúrate de copiar la URL completa.")
        return
    
    # 4. Intercambiar código por token
    exchange_code_for_token(code, code_verifier)

if __name__ == "__main__":
    main()
