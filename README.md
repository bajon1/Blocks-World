# Blocks World

Projekt rozwiązuje problem przekształcania układu ponumerowanych klocków
w układ docelowy. Obsługiwane są zasady podstawowe (`basic`) i rozszerzone
(`extended`).

## Instalacja

Wymagany jest Python 3.13 oraz `uv`.

```powershell
uv sync
```

## Format problemu

Plik zawiera dwa stany: początkowy i docelowy. Puste linie oraz linie
zaczynające się od `#` są pomijane. Liczba na pozycji `i` wskazuje klocek,
na którym leży klocek `i`; `0` oznacza stół.

```text
# start
0 1 0 2 3
# goal
2 3 4 5 0
```

Przykład znajduje się w `data/data_manual.txt`.

## Komendy

Sprawdzenie i wyświetlenie problemu:

```powershell
uv run b-problems data/data_manual.txt basic
```

Wygenerowanie wymaganych 5 problemów dla każdego `N` od 3 do 15:

```powershell
uv run b-generate --seed 42 --count 5 --min-blocks 3 --max-blocks 15 --output data/generated/seed_42/base
```

Wygenerowanie 10 problemów `N=8` do porównania DFS i BFS:

```powershell
uv run b-generate --seed 42 --count 10 --min-blocks 8 --max-blocks 8 --variant extended --output data/generated/seed_42/n8_extended
```

## Algorytmy i integracja

Każdy solver zwraca uzgodniony `SearchResult` z polami `moves`, `visited`
i `is_solved`. Pole `visited` oznacza liczbę rozwiniętych węzłów. Dostępne są:

- `dfs` — iteracyjny DFS kolegi z backtrackingiem, globalnym zbiorem
  odwiedzonych stanów i deterministyczną kolejnością generatora ruchów;
- `bfs` — BFS gwarantujący najkrótszą sekwencję;
- `ida_star` — IDA* z heurystyką `misplaced_supports` albo
  `misplaced_supports_with_blockers`.

Każdy solver przyjmuje nazwany argument `max_expanded`. IDA* przyjmuje też
`heuristic`. Pomiar pamięci może zostać dodany osobno, bez zmiany uzgodnionego
`SearchResult`.

Rozwiązanie pojedynczego problemu:

```powershell
uv run b-solve data/data_manual.txt extended bfs --max-expanded 1000000
```

Przykład IDA*:

```powershell
uv run b-solve data/data_manual.txt extended ida_star --heuristic misplaced_supports_with_blockers --max-expanded 1000000
```

Kod wyjścia `0` oznacza zweryfikowane rozwiązanie, `2` osiągnięcie limitu,
a `1` błąd danych, konfiguracji albo weryfikacji.

## Eksperymenty i raport

Pełny zestaw 135 uruchomień wymaganych dla progu 8 punktów wykonuje:

```powershell
uv run python experiments/run_experiments.py --second-heuristic misplaced_supports_with_blockers
```

Skrypt zapisuje jeden plik `output/results.json`, który jest źródłem danych
dla notebooka. Zapis jest aktualizowany po każdym z 135 eksperymentów, więc
przerwanie długiego przebiegu nie usuwa ukończonych pomiarów.

Wykonanie notebooka i zapisanie tabel oraz wniosków:

```powershell
uv run --with nbclient --with nbformat jupyter execute experiments/experiment_4_4.ipynb --inplace
```

Notebook wymaga kompletnego zestawu 135 rekordów i kończy się błędem przy
brakujących danych, niepoprawnym rozwiązaniu albo braku pomiarów pamięci.

## Testy

```powershell
uv run pytest tests -q -p no:cacheprovider
```

Notebook `experiments/experiment_4_4.ipynb` jest raportem i wczytuje wyniki
z `output/results.json` po uruchomieniu eksperymentów.
