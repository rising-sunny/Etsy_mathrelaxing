"""
lulu_ops.py — self-contained Lulu production helpers for the math gallery book
(no fitz dependency; uses requests + boto3). Credentials come from
lulu_books/.env (gitignored). NEVER commit that file.

Commands:
    python lulu_ops.py dims  <sku> <page_count>
        -> POST /cover-dimensions/  (full-wrap width/height, incl. spine)
    python lulu_ops.py validate <interior.pdf> <sku>
        -> upload the PDF to R2, POST /validate-interior/, poll to completion,
           then delete the temp object.

Notes
-----
* cover-dimensions and validate-interior are read-only checks: they place NO
  order and cost nothing. Creating a print job WOULD cost money — not done here.
* Chosen product SKU for this book (8.5x8.5 hardcover, premium color, coated,
  matte): 0850X0850.FC.PRE.CW.080CW444.MXX  (dots optional).
"""
import base64
import os
import secrets
import sys
import time

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ENV_PATH = os.path.join(REPO, "lulu_books", ".env")
CA = "/root/.ccr/ca-bundle.crt" if os.path.exists("/root/.ccr/ca-bundle.crt") else True


def load_env():
    env = {}
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def _base(env):
    sb = env.get("LULU_SANDBOX", "0") in ("1", "true", "True")
    return "https://api.sandbox.lulu.com" if sb else "https://api.lulu.com"


def token(env):
    base = _base(env)
    h = {"Authorization": "Basic " + base64.b64encode(
        f"{env['LULU_CLIENT_KEY']}:{env['LULU_CLIENT_SECRET']}".encode()).decode()}
    r = requests.post(base + "/auth/realms/glasstree/protocol/openid-connect/token",
                      headers=h, data={"grant_type": "client_credentials"}, timeout=40, verify=CA)
    r.raise_for_status()
    return r.json()["access_token"]


def _headers(env):
    return {"Authorization": "Bearer " + token(env), "Content-Type": "application/json",
            "Cache-Control": "no-cache"}


def cover_dimensions(sku, pages):
    env = load_env(); base = _base(env)
    r = requests.post(base + "/cover-dimensions/", headers=_headers(env),
                      json={"pod_package_id": sku, "interior_page_count": int(pages), "unit": "pt"},
                      timeout=60, verify=CA)
    r.raise_for_status(); d = r.json()
    w, h = float(d["width"]), float(d["height"])
    print(f"wrap: {w:.1f} x {h:.1f} pt = {w/72:.3f} x {h/72:.3f} in")
    return d


def _r2_client(env):
    import boto3
    from botocore.config import Config
    return boto3.client("s3", endpoint_url=env["R2_ENDPOINT_URL"],
                        aws_access_key_id=env["R2_ACCESS_KEY_ID"],
                        aws_secret_access_key=env["R2_SECRET_ACCESS_KEY"],
                        region_name="auto",
                        config=Config(proxies={"https": os.environ.get("HTTPS_PROXY")}),
                        verify=CA)


def validate_interior(pdf_path, sku):
    env = load_env(); base = _base(env)
    s3 = _r2_client(env)
    key = f"mathbook-validate/{secrets.token_hex(6)}/interior.pdf"
    s3.upload_file(pdf_path, env["R2_BUCKET"], key, ExtraArgs={"ContentType": "application/pdf"})
    url = env["R2_PUBLIC_URL_BASE"].rstrip("/") + "/" + key
    print("uploaded ->", url)
    try:
        H = _headers(env)
        r = requests.post(base + "/validate-interior/", headers=H,
                          json={"source_url": url, "pod_package_id": sku}, timeout=60, verify=CA)
        r.raise_for_status(); vid = r.json()["id"]
        print("validation id:", vid)
        for _ in range(24):
            time.sleep(8)
            g = requests.get(base + f"/validate-interior/{vid}/", headers=H, timeout=40, verify=CA).json()
            st = g.get("status"); print("  poll:", st)
            if st in ("VALIDATED", "NORMALIZED", "ERROR"):
                print("errors:", g.get("errors"), "| pages:", g.get("page_count"))
                return g
    finally:
        s3.delete_object(Bucket=env["R2_BUCKET"], Key=key)
        print("cleaned temp R2 object")


def main(argv):
    if len(argv) >= 3 and argv[0] == "dims":
        cover_dimensions(argv[1], argv[2])
    elif len(argv) >= 3 and argv[0] == "validate":
        validate_interior(argv[1], argv[2])
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
