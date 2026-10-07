# Knight Search Lab — five pathfinding algorithms on an 8×8 board

Two runnable views of the same problem: find the shortest knight path with BFS, DFS, A*, Greedy, or Bidirectional BFS. Both views are self-contained — open the file and run it, no installs.

## Quick path

1. **Browser (recommended):** open `index.html` directly (`file://` works — all assets are inline).
2. **Terminal:** `python3 knight_wave.py a1 h8 --fast` (add `--compare` for the metrics table, `--algo="A*"` to pick an algorithm).
3. **Test:** `python3 test_knight.py` → `9/9 passed` (~1s, zero dependencies; pytest-compatible if installed).

## Details

| Entry point | What it shows |
|-------------|---------------|
| `index.html` | Retro visualizer: step-by-step waves, per-algorithm lesson text, COMPARE table with moves / squares visited / timing bars. |
| `knight_wave.py` | Terminal reference: animated waves, `--compare` (moves, visited, `#` bars), same five algorithms as the HTML. |
| `test_knight.py` | Property tests against an independent BFS oracle: all five algorithms walk knights legally on every one of the 4096 pairs; BFS/A*/BI-BFS hit the true distance; the heuristic is admissible and 1-Lipschitz. |
| `odd/tasks/` | Working tracker for this exercise. |

## Why this shape

| Decision | Reasoning |
|----------|-----------|
| Single-file HTML, no framework | A static board with a few thousand DOM ops does not justify React plus a build step. It runs from `file://` with zero installs. |
| Two ports (JS + Python), not one | Intentional: the browser is the demo, Python is the reference you read and test. Same contract in both — see the header comments. |
| Heuristic `max(ceil(max(dr,dc)/2), ceil((dr+dc)/3))` | Admissible (never overestimates) and 1-Lipschitz — exactly what makes A* optimal. Both properties are asserted in the tests. |
| Tests bring their own oracle | The suite re-implements distances with its own BFS and its own knight moves, so a shared bug cannot hide from itself. |

Both implementations share one contract: BFS, DFS, A*, and Greedy are frontier swaps over a single `search()` skeleton; Bidirectional BFS is its own two-wave pass. Optimal set: **BFS, A*, BI-BFS** (6 moves a1→h8).

## Checklist

- [ ] `index.html` opens from disk with no network requests
- [ ] `python3 test_knight.py` → `9/9 passed`
- [ ] `python3 knight_wave.py --check` → `selfcheck ok`
- [ ] `python3 knight_wave.py a1 h8 --compare` → BFS/A*/GREEDY/BI-BFS tie at 6 moves, DFS costs 20

## Next step

Play: pick random squares in the web demo and COMPARE the five algorithms on them — a1→h8 is only one pair.
