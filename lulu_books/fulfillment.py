"""
fulfillment.py — Lulu POD order fulfillment automation for MathRelaxing's
4 physical coloring books (Hyperbolic Gardens, Fractal Flora, Sacred Geometry
& Topology, Voronoi Gardens).

Flow
----
1. list_new_orders()   -- poll Etsy receipts (requires transactions_r scope),
   keep only line items for our 4 physical listing_ids, skip receipt_ids
   already recorded in the local state file (output/fulfillment_state.json).
2. prepare_order(receipt, txn) -- for each new line item: upload that book's
   print-ready interior+cover PDFs to Cloudflare R2 (skipped if already
   uploaded -- content is static per book, not per order) and build the
   Lulu create_print_job payload (buyer address, quantity, file URLs).
   Writes the staged order to output/pending_orders.json.
3. submit_order(receipt_id) -- calls LuluClient.create_print_job(), sending
   the interior/cover URLs and shipping address to Lulu. check_and_prepare()
   calls this automatically for every new order -- no local confirmation
   step. That's safe because a print job created via the Lulu Print API is
   created in UNPAID status and Lulu holds it out of production until a
   human pays it by hand in the Lulu Print Job Portal
   (developers.lulu.com) -- confirmed 2026-07-07 there is no card on file,
   so create_print_job() cannot auto-charge. The human confirmation/payment
   step still happens, just on Lulu's side instead of in this chat.

Safety
------
This only stays safe as long as no payment method is ever added to the Lulu
account. If a card is added there, Lulu may auto-charge/auto-produce on
create_print_job(), and the automatic check->submit call below would need a
local confirmation gate added back in before running unattended again.

Usage
-----
  python fulfillment.py check      # poll for new orders, stage AND submit to Lulu (lands UNPAID)
  python fulfillment.py list       # show staged/submitted orders and their Lulu job state
  python fulfillment.py submit RECEIPT_ID   # (re)submit one order manually, e.g. after a partial failure
"""
import json
import os
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_ROOT)
sys.path.insert(0, os.path.join(_ROOT, "lulu_api"))
sys.path.insert(0, _REPO_ROOT)  # repo root, for etsy_manager
import lulu_publish as lp
import etsy_manager
# etsy_manager.TOKEN_FILE is a bare relative filename (assumes cwd == repo
# root); fulfillment.py may run from any cwd (e.g. a scheduled job), so
# repoint it at the real location instead of relying on the caller's cwd.
etsy_manager.TOKEN_FILE = os.path.join(_REPO_ROOT, "etsy_token.json")
from etsy_manager import EtsyManager

import boto3
from botocore.client import Config as BotoConfig

STATE_PATH = os.path.join(_ROOT, "output", "fulfillment_state.json")
PENDING_PATH = os.path.join(_ROOT, "output", "pending_orders.json")

# listing_id -> book config. Interior/cover paths are the print-ready PDFs
# already built (with blank-after-each pages) by each book's own generator.
POD_PACKAGE_ID = lp.PRESETS["letter_bw_pb"].pod_package_id
BOOKS = {
    4533722112: dict(
        slug="hyperbolic_gardens", title="Hyperbolic Gardens Coloring Book",
        page_count=104,
        interior=os.path.join(_ROOT, "output", "hyperbolic-gardens", "interior.pdf"),
        cover=os.path.join(_ROOT, "output", "hyperbolic-gardens", "cover.pdf"),
    ),
    4533708985: dict(
        slug="fractal_flora", title="Fractal Flora Coloring Book",
        page_count=104,
        interior=os.path.join(_ROOT, "output", "fractal-flora-coloring-book", "interior.pdf"),
        cover=os.path.join(_ROOT, "output", "fractal-flora-coloring-book", "cover.pdf"),
    ),
    4533709025: dict(
        slug="sacred_math", title="Sacred Geometry & Topology Coloring Book",
        page_count=108,
        interior=os.path.join(_ROOT, "output", "sacred-math-coloring-book", "interior.pdf"),
        cover=os.path.join(_ROOT, "output", "sacred-math-coloring-book", "cover.pdf"),
    ),
    4533709063: dict(
        slug="voronoi_gardens", title="Voronoi Gardens Coloring Book",
        page_count=104,
        interior=os.path.join(_ROOT, "output", "digital", "voronoi", "VoronoiGardens_interior_print.pdf"),
        cover=os.path.join(_ROOT, "output", "digital", "voronoi", "VoronoiGardens_cover_print.pdf"),
    ),
}


def _load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH) as f:
            return json.load(f)
    return {"processed_receipt_ids": [], "uploaded_urls": {}}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def _load_pending():
    if os.path.exists(PENDING_PATH):
        with open(PENDING_PATH) as f:
            return json.load(f)
    return {}


def _save_pending(pending):
    os.makedirs(os.path.dirname(PENDING_PATH), exist_ok=True)
    with open(PENDING_PATH, "w") as f:
        json.dump(pending, f, indent=2)


def _r2_client():
    env = lp.load_env()
    return boto3.client(
        "s3",
        endpoint_url=env["R2_ENDPOINT_URL"],
        aws_access_key_id=env["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=env["R2_SECRET_ACCESS_KEY"],
        config=BotoConfig(signature_version="s3v4"),
        region_name="auto",
    ), env["R2_BUCKET"], env["R2_PUBLIC_URL_BASE"]


def upload_to_r2(local_path, key, state):
    """Idempotent: skips the actual upload if we've already hosted this exact
    key (book files are static, so this only uploads once per book, ever,
    not once per order)."""
    if key in state["uploaded_urls"]:
        return state["uploaded_urls"][key]
    client, bucket, public_base = _r2_client()
    with open(local_path, "rb") as f:
        client.put_object(Bucket=bucket, Key=key, Body=f, ContentType="application/pdf")
    url = f"{public_base}/{key}"
    state["uploaded_urls"][key] = url
    _save_state(state)
    print(f"  Subido a R2: {key} -> {url}")
    return url


def list_new_orders():
    """Return [(receipt, transaction, book_cfg), ...] for paid receipts that
    contain one of our 4 physical listing_ids and haven't been processed yet."""
    state = _load_state()
    em = EtsyManager()
    shop_id = em.get_shop_id()
    resp = em.make_request("GET", f"/shops/{shop_id}/receipts?was_paid=true&limit=50")
    new = []
    for receipt in resp.get("results", []):
        rid = receipt["receipt_id"]
        if rid in state["processed_receipt_ids"]:
            continue
        for txn in receipt.get("transactions", []):
            book_cfg = BOOKS.get(txn.get("listing_id"))
            if book_cfg:
                new.append((receipt, txn, book_cfg))
    return new


def prepare_order(receipt, txn, book_cfg):
    """Stage a Lulu print-job payload for one line item (upload files, build
    the request body, record it in pending_orders.json). Does not itself
    call Lulu -- see submit_order()."""
    state = _load_state()
    interior_url = upload_to_r2(book_cfg["interior"], f"{book_cfg['slug']}/interior.pdf", state)
    cover_url = upload_to_r2(book_cfg["cover"], f"{book_cfg['slug']}/cover.pdf", state)

    shipping_address = {
        "name": receipt["name"],
        "street1": receipt["first_line"],
        "street2": receipt.get("second_line") or "",
        "city": receipt["city"],
        "state_code": receipt.get("state") or "",
        "postcode": receipt["zip"],
        "country_code": receipt["country_iso"],
        "phone_number": "+1 000 000 0000",  # Etsy receipts don't expose buyer phone; Lulu requires *a* value
    }
    payload = dict(
        interior_url=interior_url,
        cover_url=cover_url,
        pod_package_id=POD_PACKAGE_ID,
        quantity=txn["quantity"],
        shipping_address=shipping_address,
        contact_email=receipt.get("buyer_email") or "orders@mathrelaxing.store",
        title=book_cfg["title"],
        external_id=f"etsy-{receipt['receipt_id']}-{txn['transaction_id']}",
    )

    pending = _load_pending()
    pending[str(receipt["receipt_id"])] = {
        "receipt_id": receipt["receipt_id"],
        "transaction_id": txn["transaction_id"],
        "book": book_cfg["slug"],
        "buyer_name": receipt["name"],
        "address_summary": f"{receipt['city']}, {receipt.get('state','')} {receipt['country_iso']}",
        "quantity": txn["quantity"],
        "lulu_payload": payload,
        "submitted": False,
    }
    _save_pending(pending)

    state["processed_receipt_ids"].append(receipt["receipt_id"])
    _save_state(state)
    return pending[str(receipt["receipt_id"])]


def check_and_prepare():
    """Poll + stage + submit step, meant to run on a schedule. Automatically
    submits every new order to Lulu (create_print_job) -- safe because Lulu
    holds API-created print jobs UNPAID until a human pays them by hand in
    the Lulu Print Job Portal (no card on file, confirmed 2026-07-07). See
    module docstring."""
    new_orders = list_new_orders()
    if not new_orders:
        print("Sin pedidos nuevos.")
        return []
    submitted = []
    for receipt, txn, book_cfg in new_orders:
        print(f"\nPedido nuevo: receipt_id={receipt['receipt_id']} "
              f"libro={book_cfg['slug']} cant={txn['quantity']} "
              f"comprador={receipt['name']} ({receipt['city']}, {receipt['country_iso']})")
        order = prepare_order(receipt, txn, book_cfg)
        submit_order(order["receipt_id"])
        submitted.append(order)
    print(f"\n{len(submitted)} pedido(s) creados en Lulu (estado UNPAID).")
    print("Entra a developers.lulu.com > Print Job Portal para pagarlos y confirmar el envio.")
    return submitted


def submit_order(receipt_id):
    """Calls Lulu's create_print_job -- sends the interior/cover URLs and
    shipping address to Lulu, landing the job in UNPAID status. Does not
    itself charge anything (see module docstring for the no-card-on-file
    assumption this relies on)."""
    pending = _load_pending()
    order = pending.get(str(receipt_id))
    if not order:
        print(f"No hay pedido preparado con receipt_id={receipt_id}. Corre 'check' primero.")
        return None
    if order["submitted"]:
        print(f"El pedido {receipt_id} ya fue enviado a Lulu.")
        return None

    client = lp.make_client()
    print(f"Enviando a Lulu (queda UNPAID hasta que la pagues en el Print Job Portal): {order['book']} "
          f"x{order['quantity']} -> {order['buyer_name']} ({order['address_summary']})")
    result = client.create_print_job(**order["lulu_payload"])
    order["submitted"] = True
    order["lulu_job"] = result
    pending[str(receipt_id)] = order
    _save_pending(pending)
    print("Print job creado (UNPAID):", json.dumps(result, indent=2)[:1000])
    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "check":
        check_and_prepare()
    elif cmd == "list":
        pending = _load_pending()
        if not pending:
            print("No hay pedidos preparados.")
        for rid, o in pending.items():
            status = "ENVIADO A LULU (revisa Print Job Portal)" if o["submitted"] else "pendiente de enviar a Lulu"
            print(f"receipt_id={rid}  libro={o['book']}  x{o['quantity']}  "
                  f"comprador={o['buyer_name']} ({o['address_summary']})  [{status}]")
    elif cmd == "submit":
        if len(sys.argv) < 3:
            print("Uso: python fulfillment.py submit RECEIPT_ID")
            sys.exit(1)
        submit_order(int(sys.argv[2]))
    else:
        print(__doc__)
