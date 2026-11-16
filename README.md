# Blocks World

Solver for the Blocks World planning problem: transform an initial block arrangement into a goal arrangement using legal moves.

## Project context

- **State:** `N` numbered blocks placed on the table (`0`) or on another block. A block is clear if nothing is on it. A state is encoded as `N` integers where the *i*-th value is the support of block *i* (0 = table).
- **Variants:**
  - `basic` — allowed moves: clear block from block → table, clear block from table → clear block.
  - `extended` — also allows clear block from block → another clear block.
- **Algorithms:** DFS with backtracking (any solution, node limit), BFS (shortest sequence), IDA* (shortest sequence) with heuristics `misplaced` and `foundation`.
- **Scope:** input/validation, move generation, solution verification, dataset generation, and experiment/report tooling.

Example (`data/data_manual.txt`): start `0 1 0 2 3`, goal `2 3 4 5 0` — shortest solution is 7 moves in `basic` and 5 in `extended`.

## Installation

Requires Python 3.13 and `uv`:

```bash
uv sync
# activate (optional)
source .venv/bin/activate        # macOS/Linux
.\.venv\Scripts\Activate.ps1     # Windows PowerShell
```

Commands can also be run without activation via `uv run ...`.

## Data

Single problem (two lines: start, goal). Blank lines and lines starting with `#` are ignored:

```text
2 0 0
3 0 0
```

Batch file: one case per line as `start, goal`:

```text
2 0 0, 3 0 0
0 0 0, 0 0 2
```

Generate reproducible datasets:

```powershell
uv run b-generate --seed 42 --count 5 --min-blocks 3 --max-blocks 15 --output data/generated/seed_42/base.txt
uv run b-generate --seed 42 --count 10 --min-blocks 8 --max-blocks 8 --variant extended --output data/generated/seed_42/n8_extended.txt
```

## Solvers

```powershell
uv run b-solve data/data_manual.txt extended bfs --max-expanded 1000000
uv run b-solve data/data_manual.txt extended ida_star --heuristic foundation --max-expanded 1000000
```

IDA* requires `--heuristic` (`misplaced` or `foundation`). Output includes status, moves, length, expanded nodes, peak stored states, time, and verification.

## Experiments and report

```powershell
uv run python experiments/run_experiments.py --second-heuristic foundation
uv run --with nbclient --with nbformat jupyter execute experiments/experiment_4_4.ipynb --inplace
```

Results are written to `output/results.json`. The notebook expects a complete set of 135 records.

## Tests

```powershell
pytest
# or without activating the environment
uv run pytest tests -q -p no:cacheprovider
```
