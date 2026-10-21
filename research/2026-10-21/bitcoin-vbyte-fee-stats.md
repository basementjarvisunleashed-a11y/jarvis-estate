# Bitcoin Fee Rates per vByte — Six-Month Statistics
## Research scenario for tonight · 2026-10-21

**Coverage:** 2026-04-21 → 2026-10-21 (six months, America/Toronto).
**Commissioned by:** HgX · **Prepared by:** Research Bot, the estate's research desk.
**Unit:** satoshis per virtual byte (sat/vB) — the fee rate every Bitcoin transaction pays per unit of block space.
**Scrub statement:** this document contains only public on-chain statistics and published analytics. Nothing in it could compromise HgX — public identity only (HgX / @hgxengineering).

---

## Headline

The entire six-month window was a **floor-fee regime**. Median fee rates sat at **1.0 sat/vB** for the overwhelming majority of the period, in every month. No ordinals/runes congestion wave occurred. The largest intraday percentile spike of the window was **4.08 sat/vB** (p90, June 9). Across a 1,105-block sample (June 9 → September 9), 90.4% of block medians were ≤ 2 sat/vB and **none exceeded 7 sat/vB**.

---

## Month-by-month fee rates (sat/vB)

| Month | Median (p50) | Avg fee rate | Band (p10–p90) | Notes |
|---|---|---|---|---|
| Apr 21–30 | 1.0 flat | ~1.0–1.1 | p10/p25/p50 = 1.0; p90 briefly > 5 in congestion windows | Weekly avg medians 1.07 (Apr 2–9), 1.02 (Apr 13–19) |
| May | 1.0 every week | ~1.0 | p10/p25 pinned 1.0; p90 intraday peaks 2.13–2.99 (May 26–28) | Sharpest May intraday: May 28, ~14:00–16:00 UTC |
| Jun | 1.0; weekly avg median 1.53 (Jun 11–18) | ~1.0–1.5 | p90 card 1.1; intraday p90 peak **4.08** (Jun 9, 17:00 UTC) | Window's largest intraday spike; cleared within hours |
| Jul | avg median **1.31** | avg **1.3** | p10 1.00 / p90 1.82; peak median 2.08 | Mempool peaked 8.11 MB (~5–6 blocks backlog); cleared within hours |
| Aug | 1.0 every week | ~1.0 | p90 ≈ 1.0–1.01 | "No meaningful fee spikes"; sub-1.0 sat/vB txs clearing routinely |
| Sep | 1.0, all tiers, all month | ~1.0 | p90 intraday peak 3.15 (Sep 22); fast/30-min/economy = 2/1/1 sat/vB (Sep 29) | Fees unmoved through 6.7% price day (~$87k, Sep 21) and Bitget hack sell-off week |
| Oct 1–21 | ~1.0–1.03 | ~1.0 | next-block 2 / 30-min 1 / 1-hour 1 / economy 1 / min relay 1 (Oct 21) | Floor regime intact |

## Extremes in the window

- **Lowest:** 1.0 sat/vB median — the practical floor, observed nearly every day. Sub-1.0 sat/vB transactions began clearing routinely (Aug 2026); mempool.space minimum relay is now **0.1 sat/vB** (node policy).
- **Highest:** p90 **4.08 sat/vB** (June 9, 2026 ~17:00 UTC); highest *median* peak **2.08 sat/vB** (July). No block median exceeded 7 sat/vB in the Jun 9–Sep 9 sample.

## Notable fee events (all modest)

| Date | Event | Peak |
|---|---|---|
| 2026-04-17, 19:00–20:00 UTC | Brief median bump, April's weekly high | p50 1.63 sat/vB |
| 2026-05-28, ~14:00–16:00 UTC | Sharpest intraday of the May window; US trading-hours exchange batching suspected | p90 2.99, p50 1.19 |
| 2026-06-09, 17:00 UTC | Window's largest intraday spike; cleared within hours | p90 4.08 sat/vB |
| July 2026 | Mempool peaked 8.11 MB; cleared within hours | median peak 2.08 |
| 2026-09-21 | **Non-event:** +6.7% BTC day (~$87k), record ETF week — fees stayed at 1 sat/vB | — |
| 2026-09-24 | Bitget hack sell-off week — absorbed without fee movement | — |

No inscription/ordinals/runes congestion wave occurred in the window.

## Fee share of miner revenue (context)

| Period | Fees per block | Fee share of revenue |
|---|---|---|
| Apr 2–9 (wk sample) | 0.0160 BTC | — |
| Jul 23–30 (wk sample) | 0.0203 BTC | 0.64% |
| Sep 21 (144-block sample) | 0.0169 BTC | — |
| Oct 14 (estimate) | ~0.018 BTC | 0.64% (trailing 30d to Oct 16) |

Fees have been **under 1% of miner revenue for over a year** — the fee market is effectively dormant as a revenue source.

## Structural context

- **Relay floor lowered:** Bitcoin Core 29.1 cut the default minimum relay fee from 1 to **0.1 sat/vB**; adoption rolled out through the window. The 1 sat/vB "floor" in reports is now convention — sub-1 sat/vB transactions clear where node policy allows.
- **SegWit:** >80–85% of transactions in 2026; blocks stay 93–99% full while fees stay flat.
- **Taproot:** ~4.8% adoption / ~7.0% utilization (Sept 9, 2026) — slow, steady.
- **Governance overhang:** BIP-110 (limiting non-financial data on-chain) and an eCash fork proposal framed the August 2026 fee politics.

## Reliability notes

- btc.network reports are AI-assisted analytics — measured but secondary; cryptoscanin cross-checks mempool.space APIs. Weekly-sample monthly cells are labeled as such.
- Excluded as unreliable: Kryptoca articles (internally inconsistent figures; claimed a November 2026 halving — the next halving is ~2028). A Cointelegraph "$52 fee spike" piece was excluded as stale (June 2024, not 2026).

## Sources

- btc.network weekly fee reports and the July 2026 network-state report — https://btc.network/blog?tag=mining
- cryptoscanin fee and on-chain weekly updates — https://www.cryptoscanin.com
- thebitcoinbeacon (Sept 21 difficulty/fees) — https://thebitcoinbeacon.com
- ycharts / Blockchain.com (total fees per day) — https://ycharts.com/indicators/bitcoin_total_transaction_fees_per_day
- Cointelegraph (Core 29.1 relay-fee cut) — https://cointelegraph.com/news/bitcoin-core-default-minimum-relay-fees-decreases-90-as-update-rolls-out
- cointribune (BIP-110 / eCash fork politics) — https://www.cointribune.com

*Figures verified against primary pages on 2026-10-21 before publication. Estimates are labeled; everything else is measured historical data.*
