# Hashrate, Satoshis, and Dollars — the Full Ratio Set per Halving
## Research · 2026-10-21

**Date:** 2026-10-21
**Question asked:** dig deeper into the hashrate and mining research — work out the factors for each halving and the different ratios of hash to satoshis to US dollars for all halvings.
**Commissioned by:** HgX · **Prepared by:** Research Bot, the estate's research desk.
**Method:** halving-day hashrate (H/s) and BTC price (USD, halving-day close) from the verified 2026-10-21 hashrate study; block subsidy per epoch in satoshis (50/25/12.5/6.25/3.125 BTC). Three pairwise ratios per halving, each also expressed as a percentage of today's value, plus the multiplicative factor change between consecutive halvings.
**Scrub statement:** this document contains only public on-chain statistics and published analytics. Nothing in it could compromise HgX — public identity only (HgX / @hgxengineering).

---

## Headline

Three ratios, three stories. **Hash-per-dollar** peaked at the 2020 halving (115% of today) — reported yesterday. **Sats-per-dollar** falls every halving by construction (8.1M → 1,211). And **hash-per-subsidy-satoshi** — how much security backs each newly minted satoshi — has compounded relentlessly: **5,000 H/s per sat in 2012 → 3.39 PH/s per sat today**, a ~678-billion-fold increase, because every halving halves the subsidy while the hashrate keeps climbing.

## The three ratios per halving

| Halving | Hashrate | BTC price | Subsidy | Hash : USD (TH/s per $1) | Sats : USD (sats per $1) | Hash : sats (per subsidy-sat) |
|---|---|---|---|---|---|---|
| 2012-11-28 | 25 TH/s | $12.35 | 5.0B sats | 2.0 | 8,097,166 | 5.0 kH/s |
| 2016-07-09 | 1.56 EH/s | $651 | 2.5B sats | 2,396 | 153,610 | 624 GH/s |
| 2020-05-11 | ~129 EH/s | $8,740 | 1.25B sats | 14,760 | 11,442 | 103.2 TH/s |
| 2024-04-20 | ~650 EH/s | $64,100 | 625M sats | 10,140 | 1,560 | 1.04 PH/s |
| 2026-10-21 (today) | 1,059 EH/s | $82,600 | 312.5M sats | 12,821 | 1,211 | 3.39 PH/s |

## Each ratio as a percentage of today's value

| Halving | Hash : USD | Sats : USD | Hash : sats |
|---|---|---|---|
| 2012 | 0.02% | 668,826% | 0.00000015% |
| 2016 | 18.7% | 12,688% | 0.018% |
| 2020 | 115.1% | 945% | 3.05% |
| 2024 | 79.1% | 128.9% | 30.7% |
| Today | 100% | 100% | 100% |

## The factorials — multiplicative change between consecutive halvings

| Transition | Hash : USD | Sats : USD | Hash : sats |
|---|---|---|---|
| 2012 → 2016 | 1,184× | 0.019× | 124,800× |
| 2016 → 2020 | 6.2× | 0.074× | 165× |
| 2020 → 2024 | 0.69× | 0.136× | 10.1× |
| 2024 → today | 1.26× | 0.776× | 3.3× |

## What the factors say

- **Hash : USD** is the only ratio that ever fell between halvings (0.69× from 2020→2024) — price outran security that epoch. It is rising again (1.26× since).
- **Sats : USD** falls every halving, roughly tracking price — each halving you get ~7–50× fewer sats per dollar. It is the purest expression of Bitcoin's monetary tightening.
- **Hash : sats** never falls and compounds hardest: each halving multiplies it by hashrate-growth × 2 (the subsidy cut). The 2012→2016 jump of 124,800× is the largest single-epoch move in the dataset. Even in the quiet 2024→today stretch it grew 3.3×.

## Mining context

Miner revenue ≈ $36.79/day per PH/s (Oct 2026). Fees remain under 1% of miner revenue — the subsidy still pays for security, and each subsidy satoshi today is backed by 3.39 PH/s of work, ~33× more than at the 2024 halving.

## Reliability notes

- Hashrate and price figures are the verified 2026-10-21 dataset (halving-day readings; 3rd-halving range 121–137 EH/s — mid value 129 EH/s used; today's 1,059 EH/s confirmed live on Maketo).
- Subsidy figures are protocol constants. Ratios are arithmetic from those inputs — no estimation beyond the input readings.

## Sources

- Hashrate & price per halving: the verified 2026-10-21 halving dataset (CoinDesk/ChainBulletin, Bitinfocharts via Cointelegraph, cryptonomist.ch, Hashrate Index Q1-2024 via Nasdaq, Maketo live hashrate, Alpaca BTC/USD)
- Subsidy schedule: Bitcoin protocol (50 → 25 → 12.5 → 6.25 → 3.125 BTC)
- Miner revenue per PH/s: Maketo, Oct 2026

*Ratios computed 2026-10-21 from the verified inputs above.*
