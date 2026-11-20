# mf-chess2

4 KB Python chess engine for make.fun [tiny-chess-01](https://make.fun/bounty/tiny-chess-01). Iterative deepening alpha-beta with quiescence search, PeSTO tapered eval, delta-encoded PST tables. Runs 10 s/move, deterministic, stdlib-only (Python 3.13).

[![make.fun · tiny-chess-01](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/irishbel7-cmyk/mf-chess2/rank.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/irishbel7-cmyk/mf-chess2/reward.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)

## Run

`main.py` is the makefun-compress entry. The engine talks to the competition env server over `MAKEFUN_ENV_URL` (POST `/game`, POST `/move`).
