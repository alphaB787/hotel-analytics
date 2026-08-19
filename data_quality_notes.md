# Data Quality Notes

Source: `hotel_bookings.csv`, 119,390 rows, 32 columns. Reflects
`scripts/data_cleaning.py` as the single source of truth for cleaning
logic. This document explains and justifies what that script does, it
doesn't duplicate the rules.

## Duplicate rows — confirmed legitimate, not dropped

**~27% of rows (32,000+) look like exact duplicates across all 32
columns. The client confirmed each row represents a genuine, distinct
booking.** Thus, they are not dropped.

## Issues found and how they're handled

| # | Issue | Rows affected | Action | Rationale |
|---|---|---|---|---|
| 1 | "Duplicate" rows | ~32,000 | **Kept** | Confirmed genuine by client. |
| 2 | Zero total guests (0 adults, 0 children, 0 babies) | 180 | Dropped | A booking needs at least one guest to be meaningful — not ambiguous like zero-night bookings (below). |
| 3 | Zero total nights (0 weekend + 0 week nights) | 715 | **Kept** | See "Why zero-night bookings are kept" below. |
| 4 | Negative ADR | 1 | Dropped | Data entry error; a negative price isn't meaningful. |
| 5 | `company` NULL | 112,441 (94%) | Kept as `NaN`, `has_company` flag added | NULL means "no company," not missing data — it's meaningful. Left nullable rather than recoded to a sentinel, so the raw ID is still usable downstream if needed. |
| 6 | `agent` NULL | 16,280 (14%) | Kept as `NaN`, `has_agent` flag added | Same logic as company. |
| 7 | `country` NULL | 488 | Recoded to `'Unknown'` | Preserves the row; keeps the gap visible rather than guessing a country. |
| 8 | `children` NULL | 4 | Imputed to 0 | Overwhelming majority value; negligible impact. |

**Net effect: 119,390 → 119,209 rows (181 removed, 0.15%)** by far the
smallest cleaning footprint of any version of this project so far.

## Why zero-night bookings are kept, zero-guest bookings ware dropped

These look like the same kind of problem but aren't treated the same way,
and that's intentional, not an inconsistency.

**Zero guests (dropped):** a reservation for nobody isn't a meaningful
record under any interpretation. No further investigation needed.

**Zero nights (kept):** checked `reservation_status` for these 715 rows
before deciding:

| | Check-Out | Canceled | No-Show |
|---|---|---|---|
| Zero-night rows (715 total) | ~680 (95%) | ~22 | ~13 |

Most of these are actually **completed stays**, not cancellations likely
day-use bookings or a booking-system logging quirk, not obviously invalid
data. Since the business question here is about cancellation specifically
(not "was this a normal completed stay"), there's no reason to drop rows
based on a rule that mostly removes non-cancellations. Dropping them would
have quietly filtered the cancellation analysis on a criterion unrelated
to cancellation.

## Fields worth flagging for anyone extending this analysis

- **`agent` / `company` are left as raw nullable floats**, not recast to
  an integer ID with a 0-sentinel. This is a deliberate choice in
  `data_cleaning.py` (`has_agent`/`has_company` carry the "is there one"
  signal separately) — but anyone building a dimensional model or a
  regression on top of this needs to `fillna()` before casting to an
  integer type, since casting `NaN` directly to int will error.

## What this analysis has *not* yet checked

Worth stating plainly rather than letting a clean-looking notebook imply
more rigor than it has:

- **No confidence intervals** on the group-level cancellation rates in the
  EDA notebook or findings doc. Some groups are large (Online TA: 56,408
  bookings) and some are small (`market_segment = Undefined`: 2 bookings,
  `Refundable` deposit: 162 bookings) — the small ones shouldn't be read
  with the same confidence as the large ones, and right now nothing in the
  output makes that distinction explicit.
- **No multivariate model.** Every finding so far is a univariate cut
  (rate by one factor) plus a single stratified check (lead time within
  channel). Several candidate factors are correlated with each other
  (lead time and channel; market segment and channel) — a model that
  controls for all of them at once would show which associations hold up
  independently and which are partly the same signal counted twice.
- **No distributional check on the numeric variables** (ADR, lead_time)
  before using their means/correlations — outliers or skew could distort
  a summary statistic without it being obvious from a bar chart alone.

None of this invalidates the directional findings (lead time, channel,
guest history all show large, intuitive, and where checked robust
patterns), but the current output is a first-pass EDA, not a validated
statistical analysis, and shouldn't be presented as more final than that
without doing the above.
