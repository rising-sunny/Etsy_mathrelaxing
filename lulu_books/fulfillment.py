"""
fulfillment.py — Etsy → Lulu automatic POD for MathRelaxing physical books.

On each `check` (cron every few minutes):
  1. Poll paid, unshipped Etsy receipts (needs transactions_r on etsy_token.json).
  2. Match line items whose listing_id is in BOOKS (hardcovers + coloring books).
  3. Resolve public PDF URLs for interior + cover (store static host preferred).
  4. POST Lulu create_print_job → job lands UNPAID until paid in Print Job Portal
     (unless you add a card on file in Lulu).

Usage
-----
  python fulfillment.py register     # mapped listings + file / URL readiness
  python fulfillment.py publish-pdfs # copy local PDFs → store static/downloads/
  python fulfillment.py dry-run      # stage both hardcovers, no Lulu submit
  python fulfillment.py check        # poll Etsy → stage → submit Lulu UNPAID jobs
                                     #   + sync-tracking
  python fulfillment.py sync-tracking  # Lulu SHIPPED → push tracking to Etsy receipt
  python fulfillment.py list         # staged / submitted jobs
  python fulfillment.py submit ID    # (re)submit one receipt_id

Credentials (lulu_books/.env — never commit)
--------------------------------------------
  LULU_CLIENT_KEY / LULU_CLIENT_SECRET / LULU_SANDBOX=0
  PDF_PUBLIC_BASE  — e.g. https://mathrelaxing.store/static/downloads
                     Lulu fetches {base}/{slug}/interior.pdf and cover.pdf
  Optional R2_*    — fallback upload host if PDF_PUBLIC_BASE is unset

  repo-root etsy_token.json — scopes must include transactions_r
    (re-run: python auth.py)

Safety
------
Print jobs via Lulu Print API are UNPAID until paid in the portal (no card on
file). State files under lulu_books/output/ are gitignored.
"""
from __future__ import annotations

import json
import os
import shutil
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_ROOT)
sys.path.insert(0, os.path.join(_ROOT, "lulu_api"))
sys.path.insert(0, _REPO_ROOT)
import lulu_publish as lp
import etsy_manager

etsy_manager.TOKEN_FILE = os.path.join(_REPO_ROOT, "etsy_token.json")
from etsy_manager import EtsyManager

try:
    import boto3
    from botocore.client import Config as BotoConfig
except ImportError:  # pragma: no cover
    boto3 = None
    BotoConfig = None

STATE_PATH = os.path.join(_ROOT, "output", "fulfillment_state.json")
PENDING_PATH = os.path.join(_ROOT, "output", "pending_orders.json")

# Where publish-pdfs copies files so a VPS deploy of mathrelaxing.store exposes them.
_STORE_DOWNLOADS = os.path.normpath(
    os.path.join(_REPO_ROOT, "..", "mathrelaxing.store", "static", "downloads")
)

# ── Lulu SKUs ────────────────────────────────────────────────────────────────
SKU_LETTER_BW_PB = "0850X1100.BW.STD.PB.060UW444.MXX"  # 8.5×11 B&W paperback
SKU_SQUARE_HC_STD = "0850X0850.FC.STD.CW.080CW444.MXX"  # 8.5×8.5 color HC standard
SKU_SQUARE_HC_PREM = "0850X0850.FC.PRE.CW.080CW444.MXX"  # 8.5×8.5 color HC premium

_SOI_DIR = os.path.join(_ROOT, "generators", "concepts_gallery", "fullbook")
_TMB_DIR = os.path.join(_ROOT, "generators", "math_gallery", "fullbook")

# listing_id → book config.
# public_slug: folder under PDF_PUBLIC_BASE (and store static/downloads/).
# premium_sku_tokens: substring match on Etsy SKU / variation for PRE package.
BOOKS = {
    # ── Coloring books (letter B&W perfect bound) ──
    4533722112: dict(
        slug="hyperbolic_gardens",
        public_slug="hyperbolic-gardens",
        title="Hyperbolic Gardens Coloring Book",
        page_count=104,
        pod_package_id=SKU_LETTER_BW_PB,
        interior=os.path.join(_ROOT, "output", "hyperbolic-gardens", "interior.pdf"),
        cover=os.path.join(_ROOT, "output", "hyperbolic-gardens", "cover.pdf"),
    ),
    4533708985: dict(
        slug="fractal_flora",
        public_slug="fractal-flora-coloring-book",
        title="Fractal Flora Coloring Book",
        page_count=104,
        pod_package_id=SKU_LETTER_BW_PB,
        interior=os.path.join(_ROOT, "output", "fractal-flora-coloring-book", "interior.pdf"),
        cover=os.path.join(_ROOT, "output", "fractal-flora-coloring-book", "cover.pdf"),
    ),
    4533709025: dict(
        slug="sacred_math",
        public_slug="sacred-math-coloring-book",
        title="Sacred Geometry & Topology Coloring Book",
        page_count=108,
        pod_package_id=SKU_LETTER_BW_PB,
        interior=os.path.join(_ROOT, "output", "sacred-math-coloring-book", "interior.pdf"),
        cover=os.path.join(_ROOT, "output", "sacred-math-coloring-book", "cover.pdf"),
    ),
    4533709063: dict(
        slug="voronoi_gardens",
        public_slug="voronoi",
        title="Voronoi Gardens Coloring Book",
        page_count=104,
        pod_package_id=SKU_LETTER_BW_PB,
        interior=os.path.join(
            _ROOT, "output", "digital", "voronoi", "VoronoiGardens_interior_print.pdf"
        ),
        cover=os.path.join(
            _ROOT, "output", "digital", "voronoi", "VoronoiGardens_cover_print.pdf"
        ),
    ),
    # ── Coffee-table hardcovers (square color case-wrap) ──
    # The Shape of an Idea — draft 4548870190 ($38 / $52)
    4548870190: dict(
        slug="shape_of_an_idea",
        public_slug="shape-of-an-idea",
        title="The Shape of an Idea — Math Art Book",
        page_count=45,
        pod_package_id=SKU_SQUARE_HC_STD,
        pod_package_id_premium=SKU_SQUARE_HC_PREM,
        interior=os.path.join(_SOI_DIR, "interior.pdf"),
        cover=os.path.join(_SOI_DIR, "cover_wrap.pdf"),
        premium_sku_tokens=("PREM", "PREMIUM"),
    ),
    # The Mathematics of Beauty — active 4544209146 ($48 / $65)
    # Live SEO title: "Math Art Coffee Table Book | Hardcover Fractals…"
    4544209146: dict(
        slug="mathematics_of_beauty",
        public_slug="mathematics-of-beauty",
        title="The Mathematics of Beauty — Math Art Book",
        page_count=88,
        pod_package_id=SKU_SQUARE_HC_STD,
        pod_package_id_premium=SKU_SQUARE_HC_PREM,
        interior=os.path.join(_TMB_DIR, "interior.pdf"),
        cover=os.path.join(_TMB_DIR, "cover_wrap.pdf"),
        premium_sku_tokens=("PREM", "PREMIUM"),
    ),
}

# Hardcovers we auto-fulfill by default (coloring books share store paths already).
HARDCOVER_IDS = (4548870190, 4544209146)

PARTNER_LULU = 5702394  # Etsy production partner disclosure (Morrisville, NC)


def _load_env() -> dict:
    return lp.load_env()


def _public_base() -> str:
    env = _load_env()
    return (env.get("PDF_PUBLIC_BASE") or os.environ.get("PDF_PUBLIC_BASE") or "").rstrip("/")


def _load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"processed_receipt_ids": [], "uploaded_urls": {}, "failed_receipt_ids": {}}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def _load_pending():
    if os.path.exists(PENDING_PATH):
        with open(PENDING_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_pending(pending):
    os.makedirs(os.path.dirname(PENDING_PATH), exist_ok=True)
    with open(PENDING_PATH, "w", encoding="utf-8") as f:
        json.dump(pending, f, indent=2)


def resolve_book(txn: dict) -> dict | None:
    """Map an Etsy transaction to a book config (SKU-aware package)."""
    lid = txn.get("listing_id")
    base = BOOKS.get(lid)
    if not base:
        return None
    cfg = dict(base)
    sku = (txn.get("sku") or "").upper()
    title_var = " ".join(
        str(v.get("formatted_value") or v.get("value") or "")
        for v in (txn.get("variations") or [])
    ).upper()
    blob = sku + " " + title_var
    tokens = cfg.get("premium_sku_tokens") or ()
    if any(t in blob for t in tokens) and cfg.get("pod_package_id_premium"):
        cfg["pod_package_id"] = cfg["pod_package_id_premium"]
        cfg["edition"] = "premium"
    else:
        cfg["edition"] = "standard"
    return cfg


# ── PDF hosting ──────────────────────────────────────────────────────────────

def _r2_client():
    if boto3 is None:
        raise RuntimeError("boto3 required for R2 upload: pip install boto3")
    env = _load_env()
    needed = (
        "R2_ENDPOINT_URL", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY",
        "R2_BUCKET", "R2_PUBLIC_URL_BASE",
    )
    missing = [k for k in needed if not env.get(k)]
    if missing:
        raise RuntimeError(f"Missing R2 keys in lulu_books/.env: {', '.join(missing)}")
    return (
        boto3.client(
            "s3",
            endpoint_url=env["R2_ENDPOINT_URL"],
            aws_access_key_id=env["R2_ACCESS_KEY_ID"],
            aws_secret_access_key=env["R2_SECRET_ACCESS_KEY"],
            config=BotoConfig(signature_version="s3v4"),
            region_name="auto",
        ),
        env["R2_BUCKET"],
        env["R2_PUBLIC_URL_BASE"].rstrip("/"),
    )


def upload_to_r2(local_path, key, state):
    """Idempotent R2 upload."""
    if key in state["uploaded_urls"]:
        return state["uploaded_urls"][key]
    if not os.path.isfile(local_path):
        raise FileNotFoundError(f"Print file missing: {local_path}")
    client, bucket, public_base = _r2_client()
    with open(local_path, "rb") as f:
        client.put_object(Bucket=bucket, Key=key, Body=f, ContentType="application/pdf")
    url = f"{public_base}/{key}"
    state["uploaded_urls"][key] = url
    _save_state(state)
    print(f"  Subido a R2: {key} -> {url}")
    return url


def resolve_print_urls(book_cfg: dict, state: dict | None = None) -> tuple[str, str]:
    """Return (interior_url, cover_url) Lulu can fetch.

    Priority:
      1. PDF_PUBLIC_BASE + public_slug  (mathrelaxing.store static — preferred)
      2. Cloudflare R2 upload of local files
    """
    state = state if state is not None else _load_state()
    base = _public_base()
    pub = book_cfg.get("public_slug") or book_cfg["slug"]
    if base:
        interior = f"{base}/{pub}/interior.pdf"
        cover = f"{base}/{pub}/cover.pdf"
        return interior, cover

    # R2 fallback
    slug = book_cfg["slug"]
    interior = upload_to_r2(book_cfg["interior"], f"{slug}/interior.pdf", state)
    cover = upload_to_r2(book_cfg["cover"], f"{slug}/cover.pdf", state)
    return interior, cover


def publish_pdfs(listing_ids=None, dest_root=None):
    """Copy local interior/cover PDFs into the store static/downloads tree.

    After this, deploy mathrelaxing.store to VPS so URLs under PDF_PUBLIC_BASE
    return 200. Cover is always published as cover.pdf (Lulu expects that name
    under our convention; source may be cover_wrap.pdf).
    """
    dest_root = dest_root or _STORE_DOWNLOADS
    ids = listing_ids or list(HARDCOVER_IDS)
    if not os.path.isdir(os.path.dirname(dest_root)):
        print(f"WARN: store repo not found next to Etsy repo ({dest_root})")
    os.makedirs(dest_root, exist_ok=True)
    for lid in ids:
        cfg = BOOKS.get(lid)
        if not cfg:
            print(f"  skip unknown listing {lid}")
            continue
        pub = cfg.get("public_slug") or cfg["slug"]
        out_dir = os.path.join(dest_root, pub)
        os.makedirs(out_dir, exist_ok=True)
        for label, src, name in (
            ("interior", cfg["interior"], "interior.pdf"),
            ("cover", cfg["cover"], "cover.pdf"),
        ):
            if not os.path.isfile(src):
                print(f"  MISSING {cfg['slug']} {label}: {src}")
                continue
            dst = os.path.join(out_dir, name)
            shutil.copy2(src, dst)
            print(f"  OK {pub}/{name}  ({os.path.getsize(dst) // 1024} KB) ← {src}")
    base = _public_base() or "https://mathrelaxing.store/static/downloads"
    print(f"\nDeploy store static/downloads to VPS, then Lulu can fetch:")
    print(f"  {base}/{{public_slug}}/interior.pdf")
    print(f"  {base}/{{public_slug}}/cover.pdf")


# ── Etsy → stage → Lulu ──────────────────────────────────────────────────────

def list_new_orders():
    """Return [(receipt, [(transaction, book_cfg), ...]), ...] for paid unshipped
    receipts with at least one mapped book (one Lulu job per receipt)."""
    state = _load_state()
    em = EtsyManager()
    shop_id = em.get_shop_id()
    try:
        resp = em.make_request(
            "GET",
            f"/shops/{shop_id}/receipts?was_paid=true&was_shipped=false&limit=50",
        )
    except Exception as e:
        msg = str(e)
        if "403" in msg or "scope" in msg.lower():
            raise RuntimeError(
                "Etsy receipts 403 — re-auth with transactions_r: python auth.py\n"
                f"Original: {e}"
            ) from e
        raise
    new = []
    done = set(state.get("processed_receipt_ids") or [])
    pending = _load_pending()
    for receipt in resp.get("results", []):
        rid = receipt["receipt_id"]
        if rid in done:
            continue
        # Skip if already staged/submitted for this receipt
        if str(rid) in pending and pending[str(rid)].get("submitted"):
            continue
        items = [
            (txn, cfg)
            for txn in receipt.get("transactions", [])
            if (cfg := resolve_book(txn))
        ]
        if items:
            new.append((receipt, items))
    return new


def _state_code(receipt: dict) -> str:
    """Etsy gives codes for US/CA/AU ("TX", "ON", "VIC") but full region names
    elsewhere ("West Yorkshire"); Lulu wants a code, so drop long names."""
    st = (receipt.get("state") or "").strip()
    return st.upper() if 0 < len(st) <= 3 else ""


def _shipping_from_receipt(receipt: dict) -> dict:
    return {
        "name": receipt.get("name") or "Customer",
        "street1": receipt.get("first_line") or "",
        "street2": receipt.get("second_line") or "",
        "city": receipt.get("city") or "",
        "state_code": _state_code(receipt),
        "postcode": receipt.get("zip") or "",
        "country_code": receipt.get("country_iso") or "US",
        "phone_number": receipt.get("buyer_phone") or "+1 202 555 0100",
        "email": receipt.get("buyer_email") or "orders@mathrelaxing.store",
    }


def prepare_order(receipt, items, *, mark_processed: bool = False):
    """Stage one Lulu payload for all book items [(txn, book_cfg), ...] of a
    receipt (single shipment). Does not call Lulu. Optionally marks processed."""
    state = _load_state()
    line_items = []
    for txn, book_cfg in items:
        interior_url, cover_url = resolve_print_urls(book_cfg, state)
        line_items.append(dict(
            interior_url=interior_url,
            cover_url=cover_url,
            pod_package_id=book_cfg["pod_package_id"],
            quantity=int(txn.get("quantity") or 1),
            title=book_cfg["title"],
            external_id=f"etsy-txn-{txn['transaction_id']}",
        ))
    ship = _shipping_from_receipt(receipt)
    payload = dict(
        line_items=line_items,
        shipping_address={
            k: ship[k]
            for k in (
                "name", "street1", "street2", "city", "state_code",
                "postcode", "country_code", "phone_number",
            )
        },
        contact_email=ship["email"],
        external_id=f"etsy-{receipt['receipt_id']}",
    )

    pending = _load_pending()
    entry = {
        "receipt_id": receipt["receipt_id"],
        "transaction_ids": [t["transaction_id"] for t, _ in items],
        "listing_ids": [t.get("listing_id") for t, _ in items],
        "skus": [t.get("sku") for t, _ in items],
        "editions": [c.get("edition") for _, c in items],
        "book": " + ".join(c["slug"] for _, c in items),
        "buyer_name": ship["name"],
        "address_summary": (
            f"{ship['city']}, {ship.get('state_code', '')} {ship['country_code']}"
        ),
        "quantity": sum(li["quantity"] for li in line_items),
        "lulu_payload": payload,
        "submitted": False,
    }
    pending[str(receipt["receipt_id"])] = entry
    _save_pending(pending)

    if mark_processed:
        if receipt["receipt_id"] not in state["processed_receipt_ids"]:
            state["processed_receipt_ids"].append(receipt["receipt_id"])
            _save_state(state)
    return entry


def submit_order(receipt_id):
    pending = _load_pending()
    order = pending.get(str(receipt_id))
    if not order:
        print(f"No hay pedido preparado con receipt_id={receipt_id}. Corre 'check' primero.")
        return None
    if order.get("submitted"):
        print(f"El pedido {receipt_id} ya fue enviado a Lulu.")
        return order.get("lulu_job")

    client = lp.make_client()
    print(
        f"Enviando a Lulu (UNPAID): {order['book']} x{order['quantity']} "
        f"-> {order['buyer_name']} ({order['address_summary']})"
    )
    try:
        result = client.create_print_job(**order["lulu_payload"])
    except Exception as e:
        state = _load_state()
        state.setdefault("failed_receipt_ids", {})[str(receipt_id)] = str(e)[:500]
        _save_state(state)
        print(f"ERROR Lulu create_print_job: {e}")
        raise

    order["submitted"] = True
    order["lulu_job"] = result
    pending[str(receipt_id)] = order
    _save_pending(pending)

    state = _load_state()
    rid = order["receipt_id"]
    if rid not in state["processed_receipt_ids"]:
        state["processed_receipt_ids"].append(rid)
    state.get("failed_receipt_ids", {}).pop(str(rid), None)
    _save_state(state)

    job_id = result.get("id") if isinstance(result, dict) else None
    print(f"Print job creado (UNPAID) id={job_id}")
    print(json.dumps(result, indent=2)[:1200])
    print("Paga en Lulu Print Job Portal si no hay tarjeta en archivo.")
    return result


def check_and_prepare():
    """Poll Etsy, stage, and submit Lulu jobs for every new book order."""
    new_orders = list_new_orders()
    if not new_orders:
        print("Sin pedidos nuevos de libros mapeados.")
        return []
    submitted = []
    base = _public_base()
    for receipt, items in new_orders:
        print(
            f"\nPedido nuevo: receipt_id={receipt['receipt_id']} "
            f"comprador={receipt.get('name')} "
            f"({receipt.get('city')}, {receipt.get('country_iso')})"
        )
        for txn, book_cfg in items:
            print(
                f"  - libro={book_cfg['slug']} ({book_cfg.get('edition')}) "
                f"cant={txn.get('quantity')}"
            )
        # Local files must exist if using R2; for public base only URLs matter
        missing = [] if base else [
            (label, cfg[label])
            for _, cfg in items
            for label in ("interior", "cover")
            if not os.path.isfile(cfg[label])
        ]
        if missing:
            for label, path in missing:
                print(f"  ABORT MISSING {label}: {path}")
            print("  Or set PDF_PUBLIC_BASE and deploy PDFs to the store.")
            continue
        try:
            order = prepare_order(receipt, items, mark_processed=False)
            submit_order(order["receipt_id"])
            submitted.append(order)
        except Exception as e:
            print(f"  Falló submit (se reintentará en el próximo check): {e}")
    print(f"\n{len(submitted)} pedido(s) enviados a Lulu (estado UNPAID).")
    return submitted


# ── Lulu → Etsy (status + tracking) ──────────────────────────────────────────

LULU_FAILED = ("REJECTED", "CANCELED", "ERROR")


def _lulu_tracking(job: dict) -> list[tuple[str, str]]:
    """[(tracking_code, carrier_name), ...] unique, from a Lulu print job."""
    out = []
    for li in job.get("line_items") or []:
        code = (li.get("tracking_id") or "").strip()
        if code and code not in [c for c, _ in out]:
            out.append((code, (li.get("carrier_name") or "").strip()))
    return out


def sync_tracking():
    """For submitted jobs not yet synced: read Lulu status; when SHIPPED, push
    the tracking code to the Etsy receipt (marks it shipped, notifies buyer)."""
    pending = _load_pending()
    todo = {
        rid: o for rid, o in pending.items()
        if o.get("submitted") and not o.get("tracking_synced")
        and isinstance(o.get("lulu_job"), dict) and o["lulu_job"].get("id")
    }
    if not todo:
        print("Sin trabajos Lulu pendientes de tracking.")
        return
    client = lp.make_client()
    em = EtsyManager()
    shop_id = em.get_shop_id()
    for rid, order in todo.items():
        job_id = order["lulu_job"]["id"]
        try:
            job = client.get_print_job(job_id)
        except Exception as e:
            print(f"receipt_id={rid} job={job_id}: error leyendo Lulu: {e}")
            continue
        status = (job.get("status") or {}).get("name") or "?"
        if status != order.get("lulu_status"):
            print(f"receipt_id={rid} job={job_id}: {order.get('lulu_status')} -> {status}")
        order["lulu_status"] = status
        if status in LULU_FAILED:
            msg = (job.get("status") or {}).get("messages")
            print(f"  ATENCIÓN: job {job_id} {status} — revisar en Lulu: {msg}")
        elif status == "UNPAID":
            print(f"  job {job_id} sigue UNPAID — pagar en Lulu Print Job Portal.")
        elif status == "SHIPPED":
            tracking = _lulu_tracking(job)
            if not tracking:
                print(f"  job {job_id} SHIPPED sin tracking todavía; reintento luego.")
            else:
                try:
                    receipt = em.make_request("GET", f"/shops/{shop_id}/receipts/{rid}")
                    if receipt.get("is_shipped"):
                        print(f"  Etsy receipt {rid} ya estaba enviado; no se sube tracking.")
                    else:
                        code, carrier = tracking[0]
                        em.make_request(
                            "POST",
                            f"/shops/{shop_id}/receipts/{rid}/tracking",
                            payload={"tracking_code": code, "carrier_name": carrier or "other"},
                        )
                        print(f"  Tracking subido a Etsy: {carrier} {code}")
                        if len(tracking) > 1:
                            print(f"  (varios paquetes; resto: {tracking[1:]})")
                    order["tracking"] = tracking
                    order["tracking_synced"] = True
                except Exception as e:
                    print(f"  Error subiendo tracking a Etsy (reintento luego): {e}")
        pending[rid] = order
        _save_pending(pending)


def register_status():
    """Print mapped listings and whether print files / public URLs are ready."""
    base = _public_base()
    print(f"PDF_PUBLIC_BASE = {base or '(unset — will use R2 if configured)'}")
    print(
        f"{'listing_id':<12} {'slug':<22} {'pages':>5}  interior  cover  public_urls"
    )
    print("-" * 100)
    for lid, cfg in BOOKS.items():
        i_ok = "OK" if os.path.isfile(cfg["interior"]) else "MISSING"
        c_ok = "OK" if os.path.isfile(cfg["cover"]) else "MISSING"
        pub = cfg.get("public_slug") or cfg["slug"]
        if base:
            urls = f"{base}/{pub}/{{interior,cover}}.pdf"
        else:
            urls = "R2 fallback"
        print(
            f"{lid:<12} {cfg['slug']:<22} {cfg['page_count']:>5}  "
            f"{i_ok:<8} {c_ok:<6}  {urls}"
        )
        if cfg.get("pod_package_id_premium"):
            print(
                f"{'':12} {'  + premium package':<22} {'':5}  "
                f"{'':8} {'':6}  {cfg['pod_package_id_premium']}"
            )


def dry_run_stage():
    """Stage payloads for both hardcovers without Etsy poll or Lulu submit."""
    base = _public_base()
    print(f"PDF_PUBLIC_BASE = {base or '(unset)'}")
    for lid in HARDCOVER_IDS:
        cfg = dict(BOOKS[lid])
        cfg["edition"] = "standard"
        print(f"\n--- {cfg['slug']} (listing {lid}) ---")
        for label, path in (("interior", cfg["interior"]), ("cover", cfg["cover"])):
            if os.path.isfile(path):
                print(f"  local {label}: {path} ({os.path.getsize(path) // 1024} KB)")
            else:
                print(f"  local {label}: MISSING  {path}")
        try:
            iu, cu = resolve_print_urls(cfg)
            print(f"  Lulu interior_url: {iu}")
            print(f"  Lulu cover_url:    {cu}")
        except Exception as e:
            print(f"  URL resolve error: {e}")
            continue
        fake_receipt = {
            "receipt_id": 9000000000 + lid % 100000,
            "name": "DRY RUN TEST",
            "first_line": "123 Test St",
            "second_line": "",
            "city": "Austin",
            "state": "TX",
            "zip": "78701",
            "country_iso": "US",
            "buyer_email": "orders@mathrelaxing.store",
        }
        fake_txn = {
            "transaction_id": 1,
            "listing_id": lid,
            "quantity": 1,
            "sku": "SOI-STD-8585" if lid == 4548870190 else "TMB-STD-8585",
        }
        entry = prepare_order(fake_receipt, [(fake_txn, cfg)], mark_processed=False)
        # Do not leave dry-run receipts as submitted
        pending = _load_pending()
        pending.pop(str(fake_receipt["receipt_id"]), None)
        _save_pending(pending)
        print(f"  staged external_id={entry['lulu_payload']['external_id']}")
        print(f"  pod_package_id={entry['lulu_payload']['line_items'][0]['pod_package_id']}")
    print(
        "\nDry-run complete — no Lulu print-job created. "
        "After PDFs are live at PDF_PUBLIC_BASE, real orders use: "
        "python fulfillment.py check"
    )


def ensure_etsy_partner(listing_ids=None):
    """Set Etsy production partner = Lulu on the given listings (disclosure)."""
    em = EtsyManager()
    shop = em.get_shop_id()
    for lid in listing_ids or HARDCOVER_IDS:
        try:
            em.make_request(
                "PATCH",
                f"/shops/{shop}/listings/{lid}",
                payload={
                    "who_made": "i_did",
                    "when_made": "made_to_order",
                    "is_supply": False,
                    "production_partner_ids": [PARTNER_LULU],
                },
                json_body=True,
            )
            full = em.make_request("GET", f"/listings/{lid}")
            partners = full.get("production_partners") or []
            print(f"  listing {lid}: partners={partners} state={full.get('state')}")
        except Exception as e:
            print(f"  listing {lid}: FAIL {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "check":
        check_and_prepare()
        sync_tracking()
    elif cmd == "sync-tracking":
        sync_tracking()
    elif cmd == "list":
        pending = _load_pending()
        if not pending:
            print("No hay pedidos preparados.")
        for rid, o in pending.items():
            status = (
                "ENVIADO A LULU"
                if o.get("submitted")
                else "pendiente de enviar a Lulu"
            )
            print(
                f"receipt_id={rid}  libro={o.get('book')}  x{o.get('quantity')}  "
                f"comprador={o.get('buyer_name')} ({o.get('address_summary')})  [{status}]"
            )
    elif cmd == "submit":
        if len(sys.argv) < 3:
            print("Uso: python fulfillment.py submit RECEIPT_ID")
            sys.exit(1)
        submit_order(int(sys.argv[2]))
    elif cmd == "register":
        register_status()
    elif cmd == "dry-run":
        dry_run_stage()
    elif cmd == "publish-pdfs":
        publish_pdfs()
    elif cmd == "ensure-partner":
        ensure_etsy_partner()
    else:
        print(__doc__)
        sys.exit(1)
