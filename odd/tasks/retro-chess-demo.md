# Feature: retro-chess-demo

Execution tracker for SDD change `retro-chess-demo`.
Source of truth for WHAT to build: `openspec/changes/retro-chess-demo/`
(`proposal.md`, `design.md`, `tasks.md`, `specs/`).
This file tracks execution progress, verification evidence, and the next step.

## Objective

**PIVOT (2026-10-07, user):** `index.html` must visualize the knight's BFS
**wave algorithm** (wave expansion by levels + shortest-path trace) in the
retro pixel aesthetic — NOT a playable chess game. `knight_wave.py` is the
terminal reference implementation (BFS, level colors, path trace).

## Scope (user-confirmed pivot)

- IN: 8x8 retro board, pick start/target (or preset), animated BFS wave by
  distance level, level legend, shortest-path highlight with knight hop
  animation, status panel (step/visited/path length), reset. Self-contained.
- OUT: full chess game, legal move rules, AI, sound, external assets, network.
- Files: `index.html` only (rewrite in place). `knight_wave.py` untouched.

## Delivery decision

`exception-ok` — one implementation pass. This workspace has no VCS, so chained
PR slices have no delivery meaning; the single self-contained file is one
reviewable unit. The 400-line budget is exceeded by design (single-file
constraint from the user's no-build / no-external-assets requirement).

## Tasks

Source: `openspec/changes/retro-chess-demo/tasks.md` — 24 tasks in 6 phases.

| Phase | Content | Tasks | Status | Evidence |
| ----- | ------- | ----- | ------ | -------- |
| P | Pivot: rewrite `index.html` as knight BFS wave visualizer | 1 | done | battery green, see below |

## Applicable checks

Commands defined in `openspec/changes/retro-chess-demo/tasks.md`:
`[LOGIC]`, `[STRUCT]`, `[ASSETS]`, `[VIEW]` (manual browser/projector check).
`python3 knight_wave.py --check` stays as the regression check for the
out-of-scope existing script.

## Route decisions

- sdd-init → delegated writer (openspec mode, Strict TDD false)
- sdd-explore → delegated explorer
- sdd-propose + sdd-spec + sdd-design + sdd-tasks → delegated writer (chained)
- sdd-apply → delegated writer FAILED twice (empty result / aborted); user
  dropped SDD → switched to ODD with direct writer delegation.
- implementation (`index.html`) → delegated direct writer, 1 pass.

## Next step

Manual `[VIEW]` by the user: open `index.html` — pick start/target, RUN, watch
the BFS wave expand and the knight hop the shortest path.

## Progress log

- 2026-10-07 SDD docs complete; scope confirmed (chess demo); `exception-ok`.
- 2026-10-07 Chess `index.html` written + verified; fixed 2 bad asserts in
  `selfcheck()` (`pawn ranks` checked back-rank squares, not pawn rows).
- 2026-10-07 **PIVOT** (user): demo must visualize the knight BFS wave, not a
  chess game. `index.html` rewritten in place (316 lines): pure
  `<script id="bfs-logic">` (bfs/shortestPath + selfcheck: a1→h8=6,
  monotonicity, valid knight hops, full 64-square coverage) + wiring
  (square selection, level colors, wave animation, path trace, knight hop,
  HUD step/visited/path, RUN/RESET/RANDOM).
  Battery: `[LOGIC]`=0 `[STRUCT]`=0 `[ASSETS]`=0 PARSE=0
  `python3 knight_wave.py --check`=ok (`knight_wave.py` untouched).
- 2026-10-07 RDD consent for this candidate: **DECLINED by user**
  (`declined_this_candidate`, risk medium, 1 file / 316 lines) — no review
  record created; delivery follows ordinary repository policy.
