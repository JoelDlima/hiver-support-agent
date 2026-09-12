# VirginTrains thread reconstruction report

Source: `data/raw/twcs.csv` (READ-ONLY) — Virgin subset: `author_id == "VirginTrains"`
OR text mentions `@VirginTrains` (case-insensitive).
Method: recursive `in_response_to_tweet_id` walk to root (memoised, cycle-guarded),
`created_at` sibling sort, 7-day gap split, orphan quarantine.
Output: `data/processed/virgin_threads.parquet` (65346 rows, ZSTD).

## Thread stats

| metric | value |
|---|---|
| virgin tweets | 65346 |
| threads | 15127 |
| singleton threads | 236 (0.016) |
| multi-turn threads | 14891 |
| dialogs (>=2 turns, both inbound+reply) | 14873 |
| avg thread size | 4.32 |
| max thread size | 203 |
| max depth | 74 |
| orphans quarantined | 456 (orphan rate 0.0070) |
| 7-day gap splits | 155 |
| date range | 2012-03-12 16:52:06+00:00 .. 2017-12-03 22:57:54+00:00 |

## Depth histogram (depth: count)

- depth 0: 15263
- depth 1: 16959
- depth 2: 11481
- depth 3: 7677
- depth 4: 4658
- depth 5: 3074
- depth 6: 1905
- depth 7: 1286
- depth 8: 857
- depth 9: 597

Built in 21.3s.
