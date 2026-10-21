# Hashrate per Halving, as a Percentage Ratio to Price
## Research scenario · 2026-10-21

**Date:** 2026-10-21
**Question asked:** check the hashrate for this halving, and compare it to every other halving, as a percentage ratio to the price.
**Commissioned by:** HgX · **Prepared by:** Research Bot, the estate's research desk.
**Method:** network hashrate and BTC price (USD) taken at each halving date (halving-day close for price; point reading or stated average window for hashrate), plus today's figures. For each halving, the ratio = hashrate ÷ price, expressed in TH/s per $1 of BTC price, then normalised as a percentage of today's ratio.
**Scrub statement:** this document contains only public on-chain statistics and published analytics. Nothing in it could compromise HgX — public identity only (HgX / @hgxengineering).

---

## Headline

The hashrate-per-dollar ratio **peaked at the 2020 halving** — not today. At the May 2020 halving the network carried ~14,760 TH/s per $1 of BTC price, **115% of today's ratio**. Price outran hashrate across the 2020→2024 epoch (ratio fell to 79%), and hashrate has been catching back up since (79% → 100% today). In plain terms: **Bitcoin is better secured per dollar today than at the 2024 halving, but less secured per dollar than at the 2020 halving.**

## The table — hashrate vs price at every halving

| Halving | Date | Subsidy after | Hashrate | BTC price | Ratio (TH/s per $1) | As % of today's ratio |
|---|---|---|---|---|---|---|
| 1st | 2012-11-28 | 25 BTC | ~0.000025 EH/s (25 TH/s) | ~$12.35 | 2.0 | 0.02% |
| 2nd | 2016-07-09 | 12.5 BTC | 1.56 EH/s | ~$651 | 2,396 | 18.7% |
| 3rd | 2020-05-11 | 6.25 BTC | ~129 EH/s (range 121–137) | ~$8,740 | 14,760 | 115.1% |
| 4th | 2024-04-20 | 3.125 BTC | ~650 EH/s (7-day avg ≈ 611) | ~$64,100 | 10,140 | 79.1% |
| **This halving (today)** | 2026-10-21 | 3.125 BTC | **1,059 EH/s** (daily, 20 Oct) | ~$82,600 | 12,821 | **100%** |

Reading the last column: at the 2016 halving, each dollar of BTC price was backed by only 18.7% of the hashrate-per-dollar the network carries today; at the 2020 halving it was backed by 115% — the peak.

## Epoch-to-epoch growth

| Transition | Hashrate growth | Price growth |
|---|---|---|
| 2012 → 2016 | ~62,400× | ~53× |
| 2016 → 2020 | ~83× | ~13× |
| 2020 → 2024 | ~5× | ~7× |
| 2024 → 2026 (today) | ~1.6× | ~1.3× |

Through 2020, hashrate growth outran price growth at every halving — the network was getting cheaper to attack per dollar of value secured only in the sense that both were exploding. The 2020→2024 epoch is the break: price (7×) outgrew hashrate (5×), and the per-dollar ratio fell. Since the 2024 halving, hashrate (1.6×) is again outgrowing price (1.3×).

## Current context (verified 2026-10-21)

- Hashrate 1,059 EH/s (20 Oct 2026), 7.9% below the all-time high of 1,149 EH/s (18 Oct 2025); up 13.3% in 30 days, 17.3% in 90 days.
- Hash Ribbons: all clear, no miner capitulation — the 30-day trend has sat above the 60-day trend for 55 days.
- Miner revenue ≈ $36.79/day per PH/s.

## Reliability notes

- 3rd-halving hashrate sources disagree (121 vs 137 EH/s — Blockchair vs Bitinfocharts estimation-method variance on the same day). The mid value 129 EH/s is used above; the range maps to 108–122% of today's ratio. The conclusion (2020 = peak) holds across the whole range.
- Halving-day hashrate readings are point estimates; difficulty-derived and pool-reported figures vary by method. Price figures are halving-day closes, corroborated across multiple price-history sources.
- Today's hashrate (1,059 EH/s, 20 Oct) and the ATH figures were verified against the live Maketo hashrate page on 2026-10-21.

## Sources

- Halving dates, subsidies, prices: stealthex.io, coingabbar.com, aitimeline.in, proshares.com halving brief
- Hashrate per halving: CoinDesk/ChainBulletin (2012), Bitinfocharts via Cointelegraph (2016), cryptonomist.ch / coincript.com (2020), Hashrate Index Q1-2024 via Nasdaq (2024)
- Current: Maketo Bitcoin hashrate page (verified live 2026-10-21) — https://maketo.com/bitcoin/hashrate; coincentral.com; news.bitcoin.com (Oct 2026 difficulty)
- Current price: Alpaca BTC/USD via theagenttimes.com ($82,632 at 06:30 UTC, 2026-10-21); CoinDesk live print

*Figures verified against primary pages on 2026-10-21 before publication. Ranges are labeled; everything else is measured historical data.*
