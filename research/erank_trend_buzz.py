"""
erank_trend_buzz.py — Scrape eRank Trend Buzz (yesterday / 7d / 30d).

Uses the same Edge profile as erank_edge_bulk.py (research/.edge_erank_profile).

  python research/erank_trend_buzz.py
  python research/erank_trend_buzz.py --timeframe "Past 7 Days"
  python research/erank_trend_buzz.py --filter math
  python research/erank_trend_buzz.py --out-prefix trends_wave15

Trend Buzz ≠ Bulk:
  Bulk  → avg monthly + latest month for keywords YOU paste
  Trends → top shopper searches on Etsy recently (discovery)
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import time
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout

BASE = Path(__file__).resolve().parent
PROFILE = BASE / ".edge_erank_profile"
TREND_URL = "https://members.erank.com/trend-buzz"


def parse_num(s: str | None) -> float | None:
    if s is None:
        return None
    t = str(s).strip().lower().replace(",", "")
    if t in ("", "-", "—", "n/a", "unknown", "null"):
        return None
    m = re.match(r"^([\d.]+)\s*([kmb])?$", t)
    if not m:
        try:
            return float(re.sub(r"[^\d.]", "", t) or "nan")
        except ValueError:
            return None
    val = float(m.group(1))
    suf = m.group(2)
    if suf == "k":
        val *= 1_000
    elif suf == "m":
        val *= 1_000_000
    return val


def extract_rows(page) -> list[dict]:
    """Best-effort table / text dump parse from Trend Buzz."""
    text = page.inner_text("body")
    dump = BASE / "trend_buzz_page_dump.txt"
    dump.write_text(text, encoding="utf-8")

    rows: list[dict] = []
    # Try HTML table first
    trs = page.locator("table tbody tr")
    if trs.count() == 0:
        trs = page.locator("table tr")
    for ri in range(trs.count()):
        cells = trs.nth(ri).locator("td")
        if cells.count() < 2:
            continue
        vals = [re.sub(r"\s+", " ", cells.nth(ci).inner_text()).strip() for ci in range(cells.count())]
        if not vals or vals[0].lower() in ("keyword", ""):
            continue
        # heuristic: first text-heavy cell = keyword
        kw = None
        nums = []
        for v in vals:
            if re.search(r"[a-zA-Z]", v) and not re.match(r"^[\d.,%kmb<>\s-]+$", v, re.I):
                if kw is None and v.lower() not in ("unknown", "n/a", "etsy", "usa"):
                    kw = v
                    continue
            nums.append(v)
        if not kw:
            continue
        rows.append(
            {
                "keyword": kw,
                "raw_cells": vals,
                "searches": parse_num(nums[0]) if nums else None,
                "clicks": parse_num(nums[1]) if len(nums) > 1 else None,
                "ctr": parse_num(str(nums[2]).replace("%", "")) if len(nums) > 2 else None,
                "competition": parse_num(nums[3]) if len(nums) > 3 else None,
                "kd": parse_num(nums[4]) if len(nums) > 4 else None,
            }
        )

    if len(rows) >= 5:
        return rows

    # Fallback: line-oriented scrape of dump (keyword then numbers)
    lines = [re.sub(r"\s+", " ", ln).strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]
    i = 0
    while i < len(lines) - 2:
        ln = lines[i]
        if len(ln) < 3 or ln.lower() in {
            "keyword",
            "avg. searches",
            "searches",
            "competition",
            "kd",
            "columns",
            "export",
            "trend buzz",
            "yesterday",
            "past 7 days",
            "past 30 days",
        }:
            i += 1
            continue
        # next lines look numeric?
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        if re.search(r"\d", nxt) and re.search(r"[a-zA-Z]", ln) and not re.match(r"^[\d.,%]+$", ln):
            nums = []
            j = i + 1
            while j < len(lines) and j < i + 8 and (
                re.search(r"\d", lines[j]) or lines[j].lower() in ("unknown", "< 20", "<20")
            ):
                nums.append(lines[j])
                j += 1
            if len(nums) >= 1:
                rows.append(
                    {
                        "keyword": ln,
                        "raw_cells": [ln] + nums,
                        "searches": parse_num(nums[0]) if nums else None,
                        "clicks": parse_num(nums[1]) if len(nums) > 1 else None,
                        "ctr": parse_num(str(nums[2]).replace("%", "")) if len(nums) > 2 else None,
                        "competition": parse_num(nums[3]) if len(nums) > 3 else None,
                        "kd": parse_num(nums[4]) if len(nums) > 4 else None,
                    }
                )
                i = j
                continue
        i += 1
    return rows


def score(r: dict) -> float:
    s = r.get("searches") or 0
    kd = r.get("kd")
    if s <= 0:
        return 0.0
    demand = min(100.0, (s ** 0.5) * 1.3)
    ease = max(0.0, 100 - kd) if kd is not None else 45.0
    return demand * 0.55 + ease * 0.45


def stem_relevant(kw: str) -> bool:
    k = kw.lower()
    keys = (
        "math", "calculus", "algebra", "physics", "stem", "science", "formula",
        "equation", "poster", "printable", "study", "exam", "cheat sheet",
        "teacher", "classroom", "notebook", "planner", "graph", "geometry",
        "vector", "integral", "derivative", "matrix", "digital download",
        "wall art", "student", "college", "homeschool", "lab",
    )
    return any(x in k for x in keys)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeframe", default="Past 7 Days", help='e.g. "Yesterday", "Past 7 Days", "Past 30 Days"')
    ap.add_argument("--marketplace", default="Etsy")
    ap.add_argument("--country", default="United States")
    ap.add_argument("--filter", default="", help="optional text filter if UI has search box")
    ap.add_argument("--out-prefix", default="trend_buzz")
    ap.add_argument("--login-wait", type=int, default=45)
    args = ap.parse_args()

    prefix = args.out_prefix.strip() or "trend_buzz"
    out_json = BASE / f"{prefix}.json"
    out_csv = BASE / f"{prefix}.csv"
    out_md = BASE / f"{prefix}_report.md"
    shot = BASE / f"{prefix}.png"

    PROFILE.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE),
            channel="msedge",
            headless=False,
            viewport={"width": 1400, "height": 900},
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        print("Opening Trend Buzz…")
        page.goto(TREND_URL, wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(2500)

        # login gate
        if "login" in page.url.lower() or page.get_by_text(re.compile(r"log in|sign in", re.I)).count():
            print(f"Log into eRank if needed — waiting {args.login_wait}s…")
            page.wait_for_timeout(args.login_wait * 1000)
            page.goto(TREND_URL, wait_until="domcontentloaded", timeout=90000)
            page.wait_for_timeout(2000)

        # try select timeframe (UI varies)
        for label in (args.timeframe, "Past 7 Days", "Last 7 Days", "7 Days", "Yesterday", "Past 30 Days"):
            try:
                loc = page.get_by_role("button", name=re.compile(re.escape(label), re.I))
                if loc.count():
                    loc.first.click()
                    page.wait_for_timeout(1200)
                    print("clicked timeframe:", label)
                    break
                loc = page.get_by_text(re.compile(f"^{re.escape(label)}$", re.I))
                if loc.count():
                    loc.first.click()
                    page.wait_for_timeout(1200)
                    print("clicked text timeframe:", label)
                    break
            except Exception:
                pass

        # optional filter box
        if args.filter:
            try:
                box = page.locator("input[type='search'], input[placeholder*='Filter'], input[placeholder*='Search']").first
                if box.count() or box.is_visible():
                    box.fill(args.filter)
                    page.wait_for_timeout(800)
            except Exception:
                pass

        page.wait_for_timeout(2500)
        page.screenshot(path=str(shot), full_page=True)
        print("screenshot:", shot.name)

        rows = extract_rows(page)
        print(f"parsed {len(rows)} rows")
        ctx.close()

    # rank + write
    for r in rows:
        r["score"] = round(score(r), 1)
        r["stem_relevant"] = stem_relevant(r.get("keyword") or "")

    ranked = sorted(rows, key=lambda r: r.get("score") or 0, reverse=True)
    stem = [r for r in ranked if r.get("stem_relevant")]

    out_json.write_text(json.dumps(ranked, indent=2, ensure_ascii=False), encoding="utf-8")
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["score", "keyword", "searches", "clicks", "ctr", "competition", "kd", "stem_relevant"],
            extrasaction="ignore",
        )
        w.writeheader()
        for r in ranked:
            w.writerow(r)

    lines = [
        f"# eRank Trend Buzz — {args.timeframe}",
        "",
        f"**Source:** {TREND_URL} via Edge Playwright  ",
        f"**Marketplace:** {args.marketplace} / {args.country}  ",
        f"**Rows parsed:** {len(ranked)}  ",
        f"**STEM-ish filter hits:** {len(stem)}",
        "",
        "## How to use this with Bulk + sales",
        "",
        "1. **Trend Buzz** = what shoppers searched *recently* (discovery / timing).",
        "2. **Bulk Keyword Tool** = demand + KD for *your* candidate list (validation).",
        "3. **Your sales receipts** = what *already converts* in TheMathRelaxing.",
        "",
        "Priority: sold SKUs → Trend Buzz opportunities that fit brand → Bulk to confirm KD.",
        "",
        "## Top 25 (score = recent demand × ease)",
        "",
        "| # | Keyword | Searches* | Comp | KD | STEM? | Score |",
        "|---|---------|----------:|-----:|---:|:-----:|------:|",
    ]
    for i, r in enumerate(ranked[:25], 1):
        lines.append(
            f"| {i} | {r.get('keyword')} "
            f"| {r.get('searches') if r.get('searches') is not None else '—'} "
            f"| {r.get('competition') if r.get('competition') is not None else '—'} "
            f"| {r.get('kd') if r.get('kd') is not None else '—'} "
            f"| {'yes' if r.get('stem_relevant') else ''} "
            f"| {r.get('score')} |"
        )
    lines += [
        "",
        "\\*Metric column depends on UI (often avg monthly still shown alongside rank).",
        "",
        "## STEM-relevant subset (top 20)",
        "",
        "| Keyword | Searches | KD | Score |",
        "|---------|----------:|---:|------:|",
    ]
    for r in stem[:20]:
        lines.append(
            f"| {r.get('keyword')} | {r.get('searches') if r.get('searches') is not None else '—'} "
            f"| {r.get('kd') if r.get('kd') is not None else '—'} | {r.get('score')} |"
        )
    if not stem:
        lines.append("| _(none auto-matched — open screenshot / full CSV)_ | | | |")

    lines += [
        "",
        f"Artifacts: `{out_json.name}`, `{out_csv.name}`, `{shot.name}`, `trend_buzz_page_dump.txt`",
        "",
    ]
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print("Wrote", out_md)
    print("Top 10:")
    for r in ranked[:10]:
        print(f"  {r.get('score'):5}  {r.get('keyword')}")


if __name__ == "__main__":
    main()
