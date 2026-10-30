# Blocks World

Projekt przekształca układ klocków w stan docelowy. Obsługuje warianty
`basic` i `extended` oraz algorytmy DFS, BFS i IDA*.

## Instalacja

Wymagane są Python 3.13 i `uv`:

```powershell
uv sync
.\.venv\Scripts\Activate.ps1
```

Po aktywacji środowiska polecenie `pytest` jest dostępne bezpośrednio.
Jeżeli nie chcesz aktywować środowiska, każde polecenie można uruchomić
przez `uv run`.

## Dane

Pojedynczy problem może mieć dwa wiersze:

```text
2 0 0
3 0 0
```

Plik zbiorczy zawiera jeden przypadek w każdym wierszu:

```text
2 0 0, 3 0 0
0 0 0, 0 0 2
```

Generowanie zestawów eksperymentalnych:

```powershell
uv run b-generate --seed 42 --count 5 --min-blocks 3 --max-blocks 15 --output data/generated/seed_42/base.txt
uv run b-generate --seed 42 --count 10 --min-blocks 8 --max-blocks 8 --variant extended --output data/generated/seed_42/n8_extended.txt
```

## Solvery

```powershell
uv run b-solve data/data_manual.txt extended bfs --max-expanded 1000000
uv run b-solve data/data_manual.txt extended ida_star --heuristic foundation --max-expanded 1000000
```

IDA* obsługuje heurystyki `misplaced` i `foundation`.

## Eksperymenty i raport

```powershell
uv run python experiments/run_experiments.py --second-heuristic foundation
uv run --with nbclient --with nbformat jupyter execute experiments/experiment_4_4.ipynb --inplace
```

Wyniki trafiają do `output/results.json`. Notebook wymaga kompletnych 135
rekordów.

## Testy

Po aktywacji środowiska:

```powershell
pytest
```

Bez aktywacji środowiska:

```powershell
uv run pytest tests -q -p no:cacheprovider
```
