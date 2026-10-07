#!/usr/bin/env python3
"""Knight search visualizer.

Reference implementation of five frontier-search algorithms on the 8x8 board,
with a terminal wave animation and a comparison table.

Deliberate mirror: index.html ports these same algorithms to JavaScript for the
browser demo. Keep both in sync — the contract (dist, parent, order, path) is
shared. Tests live in test_knight.py.

Usage:
    python knight_wave.py                     # random start and target, BFS
    python knight_wave.py a1 h8               # fixed squares
    python knight_wave.py a1 h8 --algo="A*"   # animate a specific algorithm
    python knight_wave.py a1 h8 --compare     # table + bars for every algorithm
    python knight_wave.py a1 h8 --fast        # no animation
    python knight_wave.py --check             # self-check
    python3 test_knight.py                    # full suite (zero dependencies)
"""
import random
import sys
import time

COLS = "abcdefgh"
MOVES = [(2, 1), (1, 2), (-1, 2), (-2, 1),
         (-2, -1), (-1, -2), (1, -2), (2, -1)]

# ponytail: palette by distance; max knight distance on 8x8 is 6, so 8 slots is plenty
LEVEL_COLORS = [46, 51, 50, 45, 40, 33, 27, 22]


def sq(name):
    return COLS.index(name[0]), int(name[1]) - 1


def label(x, y):
    return f"{COLS[x]}{y + 1}"


def h_of(a, b):
    """Admissible AND consistent lower bound on knight distance: a knight covers
    at most 2 files/ranks and 3 (dx+dy) per move, so neither term can overshoot."""
    dr, dc = abs(a[0] - b[0]), abs(a[1] - b[1])
    return max(-(-max(dr, dc) // 2), -(-(dr + dc) // 3))   # ceil division


def search(start, target, pick):
    """One skeleton, four frontier strategies — the didactic core.

    pick(frontier, dist, target) returns the index of the square to expand next:
    FIFO = BFS, LIFO = DFS, min h = greedy, min g+h = A*.
    Returns (dist, parent, order, path); path is None unless stitched by hand
    (only bidirectional does that).
    dist = depth of first discovery, order = expansion sequence with start and
    target excluded so every algorithm's count is comparable.
    """
    dist = {start: 0}
    parent = {start: None}
    done = set()
    order = []
    frontier = [start]
    while frontier:
        cur = frontier.pop(pick(frontier, dist, target))
        done.add(cur)
        if cur != start and cur != target:
            order.append(cur)
        if cur == target:
            break
        for dx, dy in MOVES:
            n = (cur[0] + dx, cur[1] + dy)
            if not (0 <= n[0] < 8 and 0 <= n[1] < 8) or n in done:
                continue
            nd = dist[cur] + 1
            if n not in dist or nd < dist[n]:   # A* may improve an open square
                dist[n] = nd
                parent[n] = cur
                if n not in frontier:
                    frontier.append(n)
    return dist, parent, order, None


def pick_fifo(frontier, dist, target):
    return 0


def pick_lifo(frontier, dist, target):
    return len(frontier) - 1


def pick_greedy(frontier, dist, target):
    return min(range(len(frontier)), key=lambda i: h_of(frontier[i], target))


def pick_astar(frontier, dist, target):
    return min(range(len(frontier)),
               key=lambda i: dist[frontier[i]] + h_of(frontier[i], target))


def bi_bfs(start, target):
    """Two BFS waves, one from each end, expanding the smaller frontier until
    they meet. dist shows each square's own wave depth (two-colour wave), the
    path is stitched across the meeting link."""
    d = [{start: 0}, {target: 0}]
    par = [{start: None}, {target: None}]
    seen = [{start: True}, {target: True}]
    frontier = [[start], [target]]
    order = []
    link = None
    while link is None and frontier[0] and frontier[1]:
        s = 0 if len(frontier[0]) <= len(frontier[1]) else 1
        o = 1 - s
        cur = frontier[s].pop(0)
        if cur != start and cur != target:
            order.append(cur)
        if cur in d[o]:
            link = (cur, cur)                     # met on this square
            break
        for dx, dy in MOVES:
            n = (cur[0] + dx, cur[1] + dy)
            if not (0 <= n[0] < 8 and 0 <= n[1] < 8) or n in seen[s]:
                continue
            if n in d[o]:
                link = (cur, n)                   # met on the edge
                break
            seen[s][n] = True
            d[s][n] = d[s][cur] + 1
            par[s][n] = cur
            frontier[s].append(n)

    dist = dict(d[0])
    for k, v in d[1].items():
        dist.setdefault(k, v)                     # start-side depth wins
    path = []
    if link is not None:
        u, v = link
        x = u if u in d[0] else v                 # x: start side, y: target side
        y = v if x == u else u
        up, c = [], x
        while c is not None:
            up.append(c)
            c = par[0][c]
        up.reverse()                              # start ... x
        down, e = [], y
        while e is not None:
            down.append(e)
            e = par[1][e]                         # y ... target
        path = up + (down[1:] if x == y else down)
    parent = {start: None}
    for i in range(1, len(path)):
        parent[path[i]] = path[i - 1]
    return dist, parent, order, path


def bfs(start, target):
    """Reference implementation: breadth-first wave (FIFO frontier)."""
    return search(start, target, pick_fifo)


ALGOS = {
    "BFS": lambda s, t: search(s, t, pick_fifo),
    "DFS": lambda s, t: search(s, t, pick_lifo),
    "A*": lambda s, t: search(s, t, pick_astar),
    "GREEDY": lambda s, t: search(s, t, pick_greedy),
    "BI-BFS": bi_bfs,
}

# algorithms proven to return a shortest path
OPTIMAL = {"BFS", "A*", "BI-BFS"}


def path_to(parent, target):
    path = []
    cell = target
    while cell is not None:
        path.append(cell)
        cell = parent[cell]
    return path[::-1]


def path_for(res, target):
    """Bidirectional hands back a stitched path; everyone else walks parent."""
    dist, parent, order, path = res
    return path if path is not None else path_to(parent, target)


def render(wave, start, target, path, max_step):
    out = ["   a  b  c  d  e  f  g  h"]
    for y in range(7, -1, -1):
        row = [f"{y + 1} "]
        for x in range(8):
            cell = (x, y)
            if cell == start:
                row.append("\033[1;30;42m S \033[0m")
            elif cell == target:
                row.append("\033[1;30;41m T \033[0m")
            elif path and cell in path:
                row.append("\033[1;30;43m * \033[0m")
            elif cell in wave and wave[cell] <= max_step:
                d = wave[cell]
                row.append(f"\033[1;30;48;5;{LEVEL_COLORS[min(d, 7)]}m {d} \033[0m")
            else:
                row.append("\033[2;37;48;235m . \033[0m")
        row.append(f" {y + 1}")
        out.append("".join(row))
    out.append("   a  b  c  d  e  f  g  h")
    return "\n".join(out)


def clear():
    print("\033[2J\033[H", end="")


def compare_table(start, target):
    """Runs every algorithm on the pair and prints moves / squares expanded / bar."""
    rows = []
    for name, fn in ALGOS.items():
        res = fn(start, target)
        rows.append((name, len(path_for(res, target)) - 1, len(res[2])))
    best = min(m for _, m, _ in rows)
    peak = max(v for _, _, v in rows) or 1
    print(f"\n {label(*start)} -> {label(*target)}   best = {best} moves")
    print(f" {'ALGO':<8} {'MOVES':>5} {'VISITED':>7}  expansion")
    for name, moves, vis in rows:
        bar = "#" * max(1, round(vis * 36 / peak)) if vis else ""
        mark = " *" if moves == best else ""
        print(f" {name:<8} {moves:>5} {vis:>7}  {bar}{mark}")
    print(" * tied for optimal\n")


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    fast = "--fast" in argv
    name = next((a.split("=", 1)[1] for a in argv if a.startswith("--algo=")), "BFS")
    if name not in ALGOS:
        sys.exit(f"unknown algo {name!r}; choose from {', '.join(ALGOS)}")
    if len(args) >= 2:
        start, target = sq(args[0]), sq(args[1])
    else:
        cells = [(x, y) for x in range(8) for y in range(8)]
        start, target = random.sample(cells, 2)

    if "--compare" in argv:
        compare_table(start, target)
        return

    res = ALGOS[name](start, target)
    wave, parent, _order, _path = res
    path = path_for(res, target)
    top = max(wave.values())                       # deepest square this search touched

    for step in range(top + 1):
        if not fast:
            clear()
        print(render(wave, start, target, None, step))
        frontier = sum(1 for v in wave.values() if v == step + 1)
        print(f"\n algo={name}  start={label(*start)}  target={label(*target)}"
              f"  step={step}/{top}"
              f"  visited={sum(1 for v in wave.values() if v <= step)}"
              f"  next_wave={frontier}")
        print(f" path so far: {' '.join(label(*c) for c in path[:step + 1])}")
        if not fast:
            time.sleep(0.6)

    clear()
    print(render(wave, start, target, path, top))
    note = "" if name in OPTIMAL else "  (not guaranteed optimal)"
    print(f"\n {name}: {len(path) - 1} moves{note}: "
          f"{' -> '.join(label(*c) for c in path)}")


def selfcheck():
    a1, h8 = sq("a1"), sq("h8")
    wave, parent, bfs_order, _ = bfs(a1, h8)
    path = path_to(parent, h8)
    assert wave[h8] == 6, wave[h8]
    assert len(wave) == 64, len(wave)               # wave discovers every square
    assert path[0] == a1 and path[-1] == h8
    assert len(path) - 1 == wave[h8]
    for a, b in zip(path, path[1:]):
        assert (b[0] - a[0], b[1] - a[1]) in MOVES, (a, b)

    def valid(p, s, t):
        if not p or p[0] != s or p[-1] != t:
            return False
        return all((b[0] - a[0], b[1] - a[1]) in MOVES for a, b in zip(p, p[1:]))

    for name, fn in ALGOS.items():
        res = fn(a1, h8)
        dist, _par, seen_order, _p = res
        p = path_for(res, h8)
        assert valid(p, a1, h8), name
        assert h8 in dist, name
        assert len(seen_order) == len(set(seen_order)), f"{name}: duplicates"
        assert a1 not in seen_order and h8 not in seen_order, f"{name}: roots"
        assert len(p) - 1 >= 6, f"{name} beat the 6-move optimum"
        if name in OPTIMAL:
            assert len(p) - 1 == 6, f"{name} must find 6, got {len(p) - 1}"
        if name == "A*":
            assert dist[h8] == 6, f"A* settled h8 at {dist[h8]}"

    assert len(ALGOS["A*"](a1, h8)[2]) <= len(bfs_order), "A* expands no more than BFS"
    assert len(bfs_order) == 62, len(bfs_order)
    solo = ALGOS["DFS"](sq("d4"), sq("d4"))
    assert path_for(solo, sq("d4")) == [sq("d4")]
    assert solo[2] == []
    print("selfcheck ok")


if __name__ == "__main__":
    if "--check" in sys.argv:
        selfcheck()
    else:
        main(sys.argv[1:])
