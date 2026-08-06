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
| **4550715355** STEM Wall Art Pack of 10 | **New pack** — high AOV $16.99 | $16.99 |
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
