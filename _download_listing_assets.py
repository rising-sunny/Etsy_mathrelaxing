"""
Download digital files + listing images for given Etsy listing IDs.

Usage:
  python _download_listing_assets.py                 # all from _batch3_remaining.json
  python _download_listing_assets.py 4536913067 ...  # specific IDs

Saves under batch3_downloads/<listing_id>/
  files/   — paid digital deliverables
  images/  — listing gallery images (for web previews)
  meta.json
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from pathlib import Path

from etsy_manager import EtsyManager

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "batch3_downloads"


def slugify(title: str) -> str:
    t = title.lower()
    t = re.sub(r"&#39;|&amp;|&quot;", "", t)
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t[:60]


def download_url(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "MathRelaxingBatch3/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        dest.write_bytes(resp.read())


def fetch_listing(m: EtsyManager, listing_id: int) -> dict:
    shop_id = m.get_shop_id()
    listing = m.make_request("GET", f"/listings/{listing_id}")
    # files
    try:
        files = m.make_request(
            "GET", f"/shops/{shop_id}/listings/{listing_id}/files"
        )
    except Exception as e:
        print(f"  files error: {e}")
        files = {"results": []}
    # images
    try:
        images = m.make_request("GET", f"/listings/{listing_id}/images")
    except Exception as e:
        print(f"  images error: {e}")
        images = {"results": []}
    return {"listing": listing, "files": files, "images": images}


def process(m: EtsyManager, listing_id: int) -> Path:
    data = fetch_listing(m, listing_id)
    listing = data["listing"]
    title = listing.get("title") or str(listing_id)
    price = listing.get("price") or {}
    amount = (price.get("amount") or 0) / (price.get("divisor") or 100)
    slug = slugify(title)

    dest = OUT / f"{listing_id}_{slug}"
    dest.mkdir(parents=True, exist_ok=True)

    meta = {
        "listing_id": listing_id,
        "title": title,
        "price": amount,
        "state": listing.get("state"),
        "url": listing.get("url"),
        "description": (listing.get("description") or "")[:2000],
        "tags": listing.get("tags"),
        "slug_guess": slug,
        "files": [],
        "images": [],
    }

    # Digital files — Etsy API returns download urls for shop owner
    for f in data["files"].get("results") or []:
        fname = f.get("filename") or f"file_{f.get('listing_file_id')}"
        # Prefer direct url fields if present
        url = (
            f.get("url")
            or f.get("download_url")
            or f.get("file_download_url")
        )
        size = f.get("size_bytes") or f.get("filesize")
        entry = {
            "filename": fname,
            "size_bytes": size,
            "listing_file_id": f.get("listing_file_id"),
            "url": url,
            "raw_keys": list(f.keys()),
        }
        meta["files"].append(entry)
        out_path = dest / "files" / fname
        if url:
            print(f"  file → {fname} ({size})")
            try:
                download_url(url, out_path)
            except Exception as e:
                print(f"    download fail: {e}")
                # try shop-scoped endpoint
                try:
                    shop_id = m.get_shop_id()
                    # Some Etsy versions expose:
                    # GET /shops/{shop_id}/listings/{listing_id}/files/{listing_file_id}
                    detail = m.make_request(
                        "GET",
                        f"/shops/{shop_id}/listings/{listing_id}/files/{f['listing_file_id']}",
                    )
                    url2 = detail.get("url") or detail.get("download_url")
                    if url2:
                        download_url(url2, out_path)
                        print(f"    retry OK via detail")
                    else:
                        print(f"    no url in detail keys={list(detail.keys())}")
                except Exception as e2:
                    print(f"    detail fail: {e2}")
        else:
            print(f"  file NO URL keys={list(f.keys())} → {fname}")
            # dump raw for debugging
            (dest / "files_meta_raw.json").write_text(
                json.dumps(data["files"], indent=2, default=str), encoding="utf-8"
            )

    # Images
    for img in data["images"].get("results") or []:
        rank = img.get("rank") or 0
        url = (
            img.get("url_fullxfull")
            or img.get("url_570xN")
            or img.get("url_fullxfull")
        )
        # pick largest available
        for k in (
            "url_fullxfull",
            "url_170x135",
            "url_570xN",
            "url_75x75",
            "url_300x300",
        ):
            if img.get(k):
                url = img[k] if k == "url_fullxfull" or not url else url
        best = None
        for k in ("url_fullxfull", "url_570xN", "url_300x300", "url_170x135"):
            if img.get(k):
                best = img[k]
                break
        if not best:
            continue
        ext = ".jpg"
        name = f"rank{rank:02d}_{img.get('listing_image_id', rank)}{ext}"
        out_path = dest / "images" / name
        print(f"  image → {name}")
        try:
            download_url(best, out_path)
            meta["images"].append({"rank": rank, "file": name, "url": best})
        except Exception as e:
            print(f"    image fail: {e}")

    (dest / "meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"  saved → {dest.relative_to(ROOT)}")
    return dest


def main():
    ids = [int(a) for a in sys.argv[1:] if a.isdigit()]
    if not ids:
        rem = ROOT / "_batch3_remaining.json"
        if not rem.exists():
            print("Run _batch3_inventory.py first, or pass listing IDs")
            sys.exit(1)
        remaining = json.loads(rem.read_text(encoding="utf-8"))
        ids = [int(x["listing_id"]) for x in remaining]

    print(f"Downloading assets for {len(ids)} listings…")
    os.chdir(ROOT)
    m = EtsyManager()
    m.get_shop_id()

    for lid in ids:
        print(f"\n=== {lid} ===")
        try:
            process(m, lid)
        except Exception as e:
            print(f"  FAILED: {type(e).__name__}: {e}")

    print("\nDone.")


if __name__ == "__main__":
    main()
