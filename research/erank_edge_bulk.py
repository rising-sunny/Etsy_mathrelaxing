"""
erank_edge_bulk.py — Open eRank Bulk Keyword Tool in Microsoft Edge via Playwright.

Uses a persistent Edge profile under research/.edge_erank_profile so your login sticks.
First run: log into eRank in the opened window if prompted, then re-run or wait.

  python research/erank_edge_bulk.py
  python research/erank_edge_bulk.py --keywords-file research/wave8_keywords.txt
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
OUT_JSON = BASE / "wave8_erank_bulk.json"
OUT_CSV = BASE / "wave8_erank_bulk.csv"
OUT_MD = BASE / "wave8_opportunity_report.md"

BULK_URL = "https://members.erank.com/bulk-keyword-tool"
# fallback marketing URL redirects if not logged in
ALT_URLS = [
    "https://erank.com/bulk-keyword-tool",
    "https://members.erank.com/keyword-tool",
]

# Broad, not math-only — digital + physical POD + printables
DEFAULT_KEYWORDS = [
    # career / business
    "resume template",
    "invoice template",
    "price list template",
    "business card template",
    "proposal template",
    "letter of recommendation",
    "freelance invoice",
    # wedding / events
    "wedding seating chart",
    "wedding table numbers",
    "bridal shower game",
    "wedding timeline",
    "baby milestone cards",
    "baby shower invitation",
    "gender reveal invitation",
    # home / life
    "chore chart for kids",
    "homeschool planner",
    "meal planner printable",
    "budget planner",
    "habit tracker",
    "cleaning schedule",
    "medication tracker",
    "password book",
    # wall art / home
    "nursery wall art",
    "bathroom wall art",
    "kitchen wall art",
    "office wall art",
    "affirmation cards",
    "welcome sign wedding",
    "custom name sign",
    # apparel POD
    "teacher sweatshirt",
    "bookish sweatshirt",
    "dog mom shirt",
    "nurse tote bag",
    # stickers
    "kindle stickers",
    "laptop stickers",
    "water bottle stickers",
    # journals
    "gratitude journal",
    "wine tasting journal",
    "reading journal",
    # creative tools
    "procreate brushes",
    "canva template",
    "etsy seller planner",
    # health
    "blood pressure log",
    "symptom tracker",
    # kids
    "reward chart",
    "potty training chart",
    # practical / blue ocean-ish
    "first aid printable",
    "emergency binder",
    "moving checklist",
    # physical home
    "funny doormat",
    "monogram doormat",
    # compare STEM we know
    "unit circle poster",
    "periodic table poster",
    "lab notebook",
]


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
    elif suf == "b":
        val *= 1_000_000_000
    return val


def parse_erank_text_dump(text: str) -> list[dict]:
    """
    Parse eRank bulk results from inner_text dump.

    eRank Bulk columns (as of 2026 UI):
      Keyword | Search Trend | Avg. Searches | Avg. Clicks | Avg. CTR |
      Etsy Competition | KD | Google Searches

    Search Trend shows the *most recent month label* (e.g. "Jun 2026") plus a
    sparkline value = searches in that latest month (NOT a weekly series).
    Avg. Searches = longer-run monthly average (eRank refreshes ~monthly).

    Pattern per row:
      <keyword>
      Mon YYYY          <- latest month in trend
      <latest-month searches>   <- spark tip / recent month volume
      <avg searches>
      <avg clicks>
      <ctr%>
      <competition>
      <kd>
      <google searches>
    """
    lines = [re.sub(r"\s+", " ", ln).strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]

    # find start after "Google Searches" header block
    start = 0
    for i, ln in enumerate(lines):
        if ln.lower() == "google searches":
            start = i + 1
    body = lines[start:]

    month_re = re.compile(
        r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}$", re.I
    )
    rows: list[dict] = []
    i = 0
    while i < len(body):
        kw = body[i]
        # skip UI chrome
        if kw.lower() in {
            "columns",
            "export",
            "filter keywords",
            "keyword",
            "search trend",
            "avg. searches",
            "avg. clicks",
            "avg. ctr",
            "etsy competition",
            "kd",
            "google searches",
            "analyze",
            "usa",
        } or kw.startswith("Quota") or kw.startswith("©"):
            i += 1
            continue
        if i + 1 >= len(body) or not month_re.match(body[i + 1]):
            i += 1
            continue
        # kw, month, latest_month_vol, avg_searches, clicks, ctr, comp, kd, google
        chunk = body[i : i + 9]
        if len(chunk) < 8:
            i += 1
            continue
        row = {
            "keyword": chunk[0],
            "trend_month": chunk[1] if len(chunk) > 1 else None,
            "latest_month_searches": chunk[2] if len(chunk) > 2 else None,
            "searches": chunk[3] if len(chunk) > 3 else None,  # Avg. Searches
            "clicks": chunk[4] if len(chunk) > 4 else None,
            "ctr": chunk[5] if len(chunk) > 5 else None,
            "competition": chunk[6] if len(chunk) > 6 else None,
            "kd": chunk[7] if len(chunk) > 7 else None,
            "google": chunk[8] if len(chunk) > 8 else None,
            "raw": chunk,
        }
        rows.append(row)
        i += 9 if len(chunk) >= 9 else 8
    return rows


def extract_table(page) -> list[dict]:
    """Scrape eRank bulk results (table cells or text dump)."""
    rows: list[dict] = []

    # 1) Try cell-by-cell on table rows
    trs = page.locator("table tbody tr")
    if trs.count() == 0:
        trs = page.locator("table tr")
    for ri in range(trs.count()):
        tr = trs.nth(ri)
        cells = tr.locator("td")
        if cells.count() < 4:
            continue
        vals = [re.sub(r"\s+", " ", cells.nth(ci).inner_text()).strip() for ci in range(cells.count())]
        # skip header-like
        if vals[0].lower() in ("keyword", ""):
            continue
        # typical: checkbox, star, keyword, trend, searches, clicks, ctr, comp, kd, google
        # find first alpha keyword cell
        kw = None
        nums = []
        for v in vals:
            if re.search(r"[a-zA-Z]", v) and not re.match(r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)", v):
                if kw is None and "%" not in v and not re.match(r"^[\d,<.]+$", v.replace(",", "")):
                    if v.lower() not in ("unknown", "n/a"):
                        kw = v
                        continue
            nums.append(v)
        if not kw:
            continue
        # map nums: often [spark/month bits, searches, clicks, ctr, comp, kd, google]
        # Prefer reading by position from full vals after keyword
        try:
            ki = vals.index(kw)
            rest = vals[ki + 1 :]
        except ValueError:
            rest = nums
        # extract numbers in order
        def take_metric(rest_list):
            for j, v in enumerate(rest_list):
                if re.search(r"\d", v) or v.lower() in ("unknown", "< 20", "<20"):
                    return v, rest_list[j + 1 :]
            return None, rest_list

        rrest = rest
        searches, rrest = take_metric(rrest)
        # skip pure month-only already handled
        clicks, rrest = take_metric(rrest)
        ctr, rrest = take_metric(rrest)
        comp, rrest = take_metric(rrest)
        kd, rrest = take_metric(rrest)
        rows.append(
            {
                "keyword": kw,
                "searches": searches,
                "clicks": clicks,
                "ctr": ctr,
                "competition": comp,
                "kd": kd,
                "raw": vals,
            }
        )

    # 2) Text dump parser (works well with eRank DOM)
    text = page.inner_text("body")
    dump_path = BASE / "wave8_erank_page_dump.txt"
    dump_path.write_text(text, encoding="utf-8")
    text_rows = parse_erank_text_dump(text)
    if len(text_rows) > len(rows):
        print(f"    (using text dump parse: {len(text_rows)} rows)")
        rows = text_rows
    elif not rows:
        print("    (no rows — dump saved)")

    return rows


def normalize_row(r: dict) -> dict:
    avg_s = parse_num(r.get("searches"))
    latest_s = parse_num(r.get("latest_month_searches"))
    # Momentum: latest month vs long-run average (>1 rising, <1 cooling)
    momentum = None
    if avg_s and avg_s > 0 and latest_s is not None:
        momentum = round(latest_s / avg_s, 2)
    return {
        "keyword": r.get("keyword") or "",
        "trend_month": r.get("trend_month"),  # e.g. "Jun 2026" — latest month eRank shows
        "latest_month_searches": latest_s,  # searches in that latest month
        "searches": avg_s,  # Avg. Searches (longer-run monthly average)
        "clicks": parse_num(r.get("clicks")),
        "ctr": parse_num(str(r.get("ctr") or "").replace("%", "")),
        "competition": parse_num(r.get("competition")),
        "kd": parse_num(r.get("kd")),
        "momentum": momentum,
        "raw": r.get("raw"),
    }


def score_row(r: dict) -> float:
    """
    Higher = better opportunity.
    Weights *current* demand (latest month) more than long-run average when available.
    """
    avg_s = r.get("searches") or 0
    latest_s = r.get("latest_month_searches")
    # Prefer recent month for demand signal; fall back to average
    s = latest_s if latest_s is not None and latest_s > 0 else avg_s
    # If latest is much higher than avg, boost; if cooling, dampen slightly
    mom = r.get("momentum")
    if mom is not None:
        if mom >= 1.15:
            s = s * 1.1
        elif mom <= 0.75:
            s = s * 0.9
    kd = r.get("kd")
    comp = r.get("competition") or 0
    ctr = r.get("ctr") or 0
    if s <= 0:
        return 0.0
    demand = min(100.0, (s ** 0.5) * 1.2)
    if kd is not None:
        ease = max(0.0, 100 - kd)
    elif comp:
        ease = max(0.0, 100 - min(100, comp / 800))
    else:
        ease = 40.0
    ctr_b = min(20.0, (ctr / 100) * 20) if ctr and ctr > 1 else min(20.0, ctr * 0.15)
    return demand * 0.45 + ease * 0.45 + ctr_b * 0.1


def write_report(rows: list[dict]):
    ranked = sorted(rows, key=score_row, reverse=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(ranked, f, indent=2, ensure_ascii=False)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "score",
                "keyword",
                "trend_month",
                "latest_month_searches",
                "searches_avg",
                "momentum",
                "clicks",
                "ctr",
                "competition",
                "kd",
            ],
        )
        w.writeheader()
        for r in ranked:
            w.writerow(
                {
                    "score": round(score_row(r), 1),
                    "keyword": r.get("keyword"),
                    "trend_month": r.get("trend_month"),
                    "latest_month_searches": r.get("latest_month_searches"),
                    "searches_avg": r.get("searches"),
                    "momentum": r.get("momentum"),
                    "clicks": r.get("clicks"),
                    "ctr": r.get("ctr"),
                    "competition": r.get("competition"),
                    "kd": r.get("kd"),
                }
            )

    # Detect which "current" month eRank returned
    months = [r.get("trend_month") for r in ranked if r.get("trend_month")]
    trend_month = months[0] if months else "unknown"

    lines = [
        "# Wave 8 — eRank Bulk (Edge)",
        "",
        f"**Source:** eRank Bulk Keyword Tool via Edge Playwright  ",
        f"**Keywords queried:** {len(rows)}  ",
        f"**Profile:** `research/.edge_erank_profile`",
        "",
        "## Time window (important)",
        "",
        "eRank Bulk does **not** expose a true “last 7 days” series in this table.",
        "What we capture:",
        "",
        f"- **`trend_month` / latest month:** eRank’s Search Trend tip — currently **{trend_month}** (searches that month).",
        "- **`searches_avg` (Avg. Searches):** longer-run monthly average (eRank refreshes ~monthly).",
        "- **`momentum`:** latest_month ÷ avg — **>1 rising**, **<1 cooling** vs the average.",
        "",
        "For week-level buzz, use eRank **Trend Buzz** separately (not bulk avg).",
        "",
        "## Ranking (recent demand × ease)",
        "",
        f"| # | Keyword | {trend_month} | Avg/mo | Mom. | Comp | KD | Score |",
        "|---|---------|----------:|-------:|-----:|-----:|---:|------:|",
    ]
    for i, r in enumerate(ranked[:40], 1):
        lines.append(
            f"| {i} | {r.get('keyword')} "
            f"| {r.get('latest_month_searches') if r.get('latest_month_searches') is not None else '—'} "
            f"| {r.get('searches') if r.get('searches') is not None else '—'} "
            f"| {r.get('momentum') if r.get('momentum') is not None else '—'} "
            f"| {r.get('competition') if r.get('competition') is not None else '—'} "
            f"| {r.get('kd') if r.get('kd') is not None else '—'} "
            f"| {score_row(r):.1f} |"
        )

    lines += [
        "",
        "## Shortlist ideas (not only math / not only digital)",
        "",
        "### A — Career templates (already started resume)",
        "- invoice / price list / proposal kits",
        "",
        "### B — Wedding & events printables",
        "- seating chart suite (stand-by), table numbers, bridal shower games",
        "",
        "### C — Kids / home systems",
        "- chore / reward charts, homeschool planner, meal planner",
        "",
        "### D — POD physical",
        "- teacher sweatshirt, funny doormat, nursery wall art (Printify/Printful)",
        "",
        "### E — Health trackers",
        "- medication / symptom / BP logs",
        "",
        "See CSV for full numbers. Re-run after login if table was empty.",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_MD}")
    print("\nTop 15 (latest month | avg | momentum | kd):")
    for r in ranked[:15]:
        print(
            f"  {score_row(r):5.1f}  latest={r.get('latest_month_searches')}  "
            f"avg={r.get('searches')}  mom={r.get('momentum')}  "
            f"kd={r.get('kd')}  [{r.get('trend_month')}]  {r.get('keyword')}"
        )


def _find_keyword_box(page):
    # wait for bulk UI
    for _ in range(40):
        loc = page.locator("textarea")
        if loc.count() > 0:
            break
        page.wait_for_timeout(250)
    else:
        raise RuntimeError("No textarea on page — are you on Bulk Keyword Tool / logged in?")
    loc = page.locator("textarea")
    best_i, best_area = 0, 0
    for i in range(min(loc.count(), 8)):
        bb = loc.nth(i).bounding_box()
        if not bb:
            continue
        area = bb["width"] * bb["height"]
        if area > best_area:
            best_area, best_i = area, i
    return loc.nth(best_i)


def fill_bulk_and_search(page, keywords: list[str]):
    """eRank Bulk allows max 20 keywords per Analyze (UI shows N/20)."""
    if len(keywords) > 20:
        raise ValueError(f"Max 20 keywords per batch, got {len(keywords)}")

    box = _find_keyword_box(page)
    text = "\n".join(keywords)
    box.click()
    box.press("Control+a")
    box.press("Backspace")
    page.wait_for_timeout(150)
    box.fill(text)
    box.evaluate(
        """(el, value) => {
            el.focus();
            el.value = value;
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        }""",
        text,
    )
    page.wait_for_timeout(600)

    analyze = page.get_by_role("button", name=re.compile(r"Analyze", re.I))
    for _ in range(25):
        if analyze.count() and analyze.first.is_enabled():
            break
        page.wait_for_timeout(250)
    else:
        # still disabled? re-type last newline
        box.click()
        page.keyboard.press("End")
        page.keyboard.type("\n", delay=30)
        page.wait_for_timeout(500)

    if analyze.count() == 0 or not analyze.first.is_enabled():
        raise RuntimeError("Analyze button still disabled (need ≤20 keywords + non-empty box)")

    analyze.first.click()
    page.wait_for_timeout(4000)
    try:
        page.wait_for_load_state("networkidle", timeout=25000)
    except PwTimeout:
        pass
    # wait until results table / rows appear
    for _ in range(30):
        if page.locator("table tbody tr").count() > 0:
            break
        if page.locator("table tr").count() > 2:
            break
        page.wait_for_timeout(500)
    page.wait_for_timeout(1500)


def run_batches(page, keywords: list[str], batch_size: int = 20) -> list[dict]:
    all_rows: list[dict] = []
    batches = [keywords[i : i + batch_size] for i in range(0, len(keywords), batch_size)]
    for bi, batch in enumerate(batches, 1):
        print(f"  Batch {bi}/{len(batches)} ({len(batch)} keywords)…")
        # return to bulk tool clean
        page.goto(BULK_URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(1500)
        fill_bulk_and_search(page, batch)
        shot = BASE / f"wave8_erank_batch{bi}.png"
        page.screenshot(path=str(shot), full_page=True)
        print(f"    screenshot {shot.name}")
        rows = extract_table(page)
        print(f"    parsed {len(rows)} rows")
        all_rows.extend(rows)
        # small pause between batches (quota-friendly)
        page.wait_for_timeout(1200)
    return all_rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keywords-file", help="Optional text file, one keyword per line")
    ap.add_argument("--headed", action="store_true", default=True)
    ap.add_argument("--login-wait", type=int, default=90, help="Seconds to wait if login needed")
    args = ap.parse_args()

    if args.keywords_file:
        keywords = [
            ln.strip()
            for ln in Path(args.keywords_file).read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.strip().startswith("#")
        ]
    else:
        keywords = DEFAULT_KEYWORDS

    PROFILE.mkdir(parents=True, exist_ok=True)
    print(f"Edge profile: {PROFILE}")
    print(f"Keywords: {len(keywords)}")
    print("Launching Microsoft Edge…")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE),
            channel="msedge",
            headless=False,
            viewport={"width": 1400, "height": 900},
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(BULK_URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(2500)
        url = page.url.lower()
        title = page.title()
        print(f"URL: {page.url}")
        print(f"Title: {title}")

        # Login wall detection
        body = ""
        try:
            body = page.inner_text("body")[:2000].lower()
        except Exception:
            pass
        if any(x in body for x in ("log in", "sign in", "login", "create free account")) and "bulk" not in body:
            print(
                f"\n*** Log into eRank in the Edge window (profile is saved). "
                f"Waiting up to {args.login_wait}s… ***\n"
            )
            deadline = time.time() + args.login_wait
            while time.time() < deadline:
                page.wait_for_timeout(3000)
                try:
                    body = page.inner_text("body")[:1500].lower()
                except Exception:
                    continue
                if "bulk" in body or "keyword" in body and "password" not in body:
                    break
            page.goto(BULK_URL, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(2000)

        # If still not on bulk, try alt
        if "bulk" not in page.url.lower():
            for u in ALT_URLS:
                try:
                    page.goto(u, wait_until="domcontentloaded", timeout=30000)
                    page.wait_for_timeout(1500)
                    if "bulk" in page.url.lower() or page.locator("textarea").count() > 0:
                        break
                except Exception:
                    continue

        print("Running bulk batches (max 20 keywords each)…")
        try:
            raw_rows = run_batches(page, keywords, batch_size=20)
        except Exception as e:
            print("Bulk error:", e)
            shot = BASE / "wave8_erank_debug.png"
            page.screenshot(path=str(shot), full_page=True)
            print(f"Screenshot: {shot}")
            try:
                (BASE / "wave8_erank_page.html").write_text(page.content(), encoding="utf-8")
            except Exception:
                pass
            context.close()
            raise

        print(f"Total raw rows: {len(raw_rows)}")
        shot = BASE / "wave8_erank_results.png"
        page.screenshot(path=str(shot), full_page=True)
        try:
            (BASE / "wave8_erank_page.html").write_text(page.content(), encoding="utf-8")
        except Exception:
            pass

        context.close()

    norm = [normalize_row(r) for r in raw_rows if r.get("keyword")]
    # de-dupe by keyword
    seen = set()
    uniq = []
    for r in norm:
        k = r["keyword"].lower()
        if k in seen:
            continue
        seen.add(k)
        uniq.append(r)
    write_report(uniq)


if __name__ == "__main__":
    main()
