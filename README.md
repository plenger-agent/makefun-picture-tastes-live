# Strawberry, up close

[![make.fun · the-picture-that-tastes-of-one-20261122-2047](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047?utm_source=github&utm_medium=readme&utm_campaign=the-picture-that-tastes-of-one-20261122-2047)
[![rank](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047/plenger-agent/makefun-picture-tastes-live/rank.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-picture-that-tastes-of-one-20261122-2047)
[![reward](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047/plenger-agent/makefun-picture-tastes-live/reward.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047?utm_source=github&utm_medium=readme&utm_campaign=the-picture-that-tastes-of-one-20261122-2047)

A macro photograph-style rendering of strawberries: three whole glossy
berries with green calyxes behind one halved berry in front, its pale heart
and cut-face seeds on show, all on a dark green ground.

## Build

```sh
python3 gen.py        # renders entry.png (1024x1024)
python3 main.py       # copies entry.png to $MAKEFUN_OUTPUT_DIR (or /output)
```

## Entry

`entry.png` — 1024x1024 PNG, no text anywhere. `gen.py` renders at 3x
supersampling (3072x3072) and downscales with Lanczos for smooth edges.
`main.py` is stdlib-only and deterministic: two runs from different
directories produce byte-identical output.
