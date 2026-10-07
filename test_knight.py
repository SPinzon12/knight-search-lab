"""Property and boundary tests for the five knight searches.

Zero dependencies — runs standalone:
    python3 test_knight.py
and is pytest-compatible if pytest is ever installed:
    python3 -m pytest test_knight.py

The oracle (exact distances) is an independent BFS written here on purpose:
tests must not trust the code under test.
"""

import sys
from collections import deque

from knight_wave import ALGOS, MOVES, OPTIMAL, h_of, sq

# Independent reference: its own copy of the knight's eight jumps, so a typo in
# the module's MOVES fails loudly instead of agreeing with itself.
ORACLE_MOVES = [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]
SQUARES = [(x, y) for x in range(8) for y in range(8)]


def _true_dist(s, t):
    """Breadth-first distance with no heuristic, no early exit, no tricks."""
    if s == t:
        return 0
    seen = {s: 0}
    q = deque([s])
    while q:
        c = q.popleft()
        for dx, dy in ORACLE_MOVES:
            n = (c[0] + dx, c[1] + dy)
            if 0 <= n[0] < 8 and 0 <= n[1] < 8 and n not in seen:
                seen[n] = seen[c] + 1
                if n == t:
                    return seen[n]
                q.append(n)
    raise AssertionError(f"unreachable square {t}")


# dist[a][g] for every pair — one pass, then plain lookups.
DIST = {a: {g: _true_dist(a, g) for g in SQUARES} for a in SQUARES}


def _is_knight_walk(path, s, t):
    if not path or path[0] != s or path[-1] != t:
        return False
    return all(
        (b[0] - a[0], b[1] - a[1]) in ORACLE_MOVES for a, b in zip(path, path[1:])
    )


def test_oracle_agrees_with_module_moves():
    """The test's moves and the module's must be the same set."""
    assert set(ORACLE_MOVES) == set(MOVES), (set(ORACLE_MOVES) ^ set(MOVES))


def test_every_algorithm_returns_a_valid_knight_walk():
    """All five algorithms, every start/target pair on the board."""
    for name, fn in ALGOS.items():
        for s in SQUARES:
            for t in SQUARES:
                res = fn(s, t)
                p = res[3] if res[3] is not None else _reconstruct(res[1], t)
                assert _is_knight_walk(p, s, t), f"{name} on {s}->{t}: {p}"


def test_optimal_algorithms_match_the_oracle():
    """BFS, A*, and bidirectional BFS must return the exact true distance."""
    for name in OPTIMAL:
        fn = ALGOS[name]
        for s in SQUARES:
            for t in SQUARES:
                res = fn(s, t)
                p = res[3] if res[3] is not None else _reconstruct(res[1], t)
                assert len(p) - 1 == DIST[s][t], (
                    f"{name} on {s}->{t}: {len(p) - 1} != {DIST[s][t]}"
                )


def test_dfs_diverges_but_still_finds_a_way():
    """DFS is allowed to be suboptimal — but it must never claim optimality."""
    p = _path(ALGOS["DFS"](sq("a1"), sq("h8")), sq("h8"))
    assert len(p) - 1 > 6, "DFS finding 6 moves would hide the lesson"
    assert _is_knight_walk(p, sq("a1"), sq("h8"))


def test_heuristic_is_admissible():
    """h must never overestimate: h(a, g) <= true distance, all pairs."""
    for a in SQUARES:
        for g in SQUARES:
            assert h_of(a, g) <= DIST[a][g], (a, g, h_of(a, g), DIST[a][g])


def test_heuristic_is_one_lipschitz():
    """Consistency: |h(a,g) - h(b,g)| <= one knight jump between a and b."""
    for a in SQUARES:
        for dx, dy in ORACLE_MOVES:
            b = (a[0] + dx, a[1] + dy)
            if not (0 <= b[0] < 8 and 0 <= b[1] < 8):
                continue
            for g in SQUARES:
                gap = abs(h_of(a, g) - h_of(b, g))
                assert gap <= 1, (a, b, g, gap)


def test_start_equals_target():
    """Degenerate pair: zero moves, empty expansion order, path is the square."""
    for name, fn in ALGOS.items():
        s = sq("d4")
        res = fn(s, s)
        assert _path(res, s) == [s], name
        assert res[2] == [], name


def test_a_star_expands_no_more_than_bfs():
    """The claim on the compare table: same guarantee, less work."""
    a1, h8 = sq("a1"), sq("h8")
    assert len(ALGOS["A*"](a1, h8)[2]) <= len(ALGOS["BFS"](a1, h8)[2])


def test_orders_are_comparable():
    """No duplicates, and start/target excluded so counts mean the same thing."""
    for name, fn in ALGOS.items():
        res = fn(sq("a1"), sq("h8"))
        order = res[2]
        assert len(order) == len(set(order)), f"{name}: duplicates"
        assert sq("a1") not in order and sq("h8") not in order, name


def _reconstruct(parent, target):
    """Local copy of the parent walk — tests do not import the module's."""
    path = [target]
    while parent[path[-1]] is not None:
        path.append(parent[path[-1]])
    path.reverse()
    return path


def _path(res, target):
    return res[3] if res[3] is not None else _reconstruct(res[1], target)


if __name__ == "__main__":
    tests = [
        (n, f)
        for n, f in sorted(globals().items())
        if n.startswith("test_") and callable(f)
    ]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"  ok    {name}")
        except AssertionError as exc:
            failed += 1
            print(f"  FAIL  {name}: {exc}")
        except Exception as exc:  # noqa: BLE001 — report, then fail the run
            failed += 1
            print(f"  ERROR {name}: {exc!r}")
    print(f"{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
