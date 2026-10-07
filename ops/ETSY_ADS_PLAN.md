# Etsy Ads plan — TheMathRelaxing

**API note:** Etsy Open API **does not** expose Ads on/off. Toggle manually in  
**Seller Hub → Marketing → Etsy Ads → Manage advertised listings**.

Regenerate candidate lists:

```bash
python ops/shop_optimize.py report
# or on VPS: cd /opt/etsy_lulu_fulfill && python shop_optimize.py report
```

## Rules

| Decision | Rule |
|----------|------|
| **ADS ON** | Has ≥1 sale **or** coffee-table book (high intent) **or** views≥25 + favs≥1 |
| **WATCH** | views 15–24, no sales yet — organic only |
| **ADS OFF** | Everything else (0-view POD, bookmarks, mugs, long-tail) |

## ADS ON now (priority order)

### Tier A — spend first (proven + traffic)

| ID | Why | Price |
|----|-----|------:|
| **4540082607** Famous Equations Set of 6 | 3 sales, 80 views, 4 favs | $3.99 |
| **4538562680** Unit Circle | 1 sale, **93** views | $3.99 |
| **4539473180** Physics Poster Set of 6 | 1 sale, 56 views | $3.99 |
| **4550715355** STEM Wall Art Pack of 10 | high AOV $16.99 | $16.99 |
| **4550737656** Physics Wall Art Pack of 10 | physics-only sibling $16.99 | $16.99 |
| **4544209146** Coffee Table Book | 33 views, 3 favs, $48 AOV | $48 |

### Tier B — light budget (has sales, lower views)

| ID | Title (short) | Price |
|----|---------------|------:|
| 4538070573 | Lab Notebook Printable | $2.99 |
| 4537623277 | Maxwell Equations print | $2.99 |
| 4534831774 | Navy Gold equations set of 8 | $3.99 |
| 4534820167 | Constants bundle set of 8 | $3.99 |
| 4537362221 | Ulam Spiral | $2.99 |
| 4537377786 | Euler Identity | $2.99 |
| 4537623005 | Black Hole | $2.99 |
| 4547949451 | Physics Field Collection II | $3.99 |
| 4547960414 | Special Functions set of 6 | $3.99 |
| 4537362085 | Golden Ratio (0 sales, 31v/3fav) | $2.99 |

### Tier C — optional / cap spend

Remaining “has_sales” listings with ≤5 views (timelines, platonic, vibrating string, planners).  
Run only if Tier A ROAS is positive.

## ADS OFF (do not enable)

- All aluminum **bookmarks** $17.99  
- **Mugs**, tote bags, canvas POD with 0 views  
- Shape of an Idea until it has organic views  
- Any listing you just paused (inactive)  
- Boho / resume / emergency binder long-tail with 0 sales  

## Daily budget suggestion (start)

| Phase | Budget | Focus |
|-------|--------|--------|
| Week 1 | $5–8/day | Tier A only |
| Week 2+ | Scale if ROAS > 1.5 | Add Tier B |

Turn **off** any listing that spends >$5 with 0 sales in 7 days.

## After pausing 30 dead listings

Shop is leaner → ads budget is less diluted. Re-check Ads manager so paused listings are not still “advertised”.

---

## Applied in Seller Hub (Playwright, 2026-08-06)

Session applied toggles on https://www.etsy.com/your/shops/me/advertising

### ADS ON (kept / confirmed)

| listing_id | Notes |
|---:|---|
| 4540082607 | Famous Equations Set of 6 (best ROAS) |
| 4538562680 | Unit Circle |
| 4539473180 | Physics Poster Set of 6 |
| 4550715355 | STEM Wall Art Pack of 10 |
| 4550737656 | Physics Wall Art Pack of 10 (enable in Ads if not auto-on) |
| 4544209146 | Coffee Table Book |
| 4538070573 | Lab Notebook |
| 4534027247 | STEM Graph Paper Notebook |
| 4537937498 | Engineering Graph Paper Planner |
| 4537362085 | Golden Ratio |
| 4534035590 | Chaos Procreate Palettes |
| 4534831774 | Navy Gold set of 8 |
| 4534820167 | Constants bundle |
| 4537362221 | Ulam Spiral |
| 4537377786 | Euler Identity print |
| 4537623277 | Maxwell |
| 4537623005 | Black Hole |
| 4547949451 | Physics Field Collection II |
| 4547960414 | Special Functions set |
| 4538061513 | Schrödinger (has sale) |

### ADS OFF (examples turned off this session)

Long-tail with spend and ROAS 0 or no sales signal: Euler poster dup `4540138522`, Grid Paper `4536990190`, LoR pack `4539149064`, B&W notebook `4536990226`, academic planner `4539457700`, boho notebook `4536971373`, Shape of an Idea `4548870190` (until organic views), plus ~35 other non-core listings (resumes, AI prompts, Morris, stickers, etc.).

### Campaign snapshot at apply time (30d panel)

- Ad views ~20.3K · spend ~$45 · attributed revenue ~$78 · **ROAS ~1.73**
- Suggested daily budget: **$5–8** focused on the ON list above.
