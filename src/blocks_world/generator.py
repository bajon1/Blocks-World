import random
from math import comb, factorial
from pathlib import Path

from .block_state import BlockState
from .io import write_problem
from .problem import BlocksProblem, Variant


def generate_state(n: int, rng: random.Random) -> BlockState:
    blocks = list(range(1, n + 1))
    rng.shuffle(blocks)

    supports = [0] * n
    available = [0]

    for block in blocks:
        support = rng.choice(available)
        supports[block - 1] = support

        if support != 0:
            available.remove(support)

        available.append(block)

    return BlockState(tuple(supports))


def generate_problems(
    n: int,
    count: int,
    rng: random.Random,
) -> list[tuple[BlockState, BlockState]]:
    if n < 3:
        raise ValueError("n must be at least 3")
    if count < 1:
        raise ValueError("count must be positive")

    state_count = sum(
        comb(n - 1, towers - 1) * factorial(n) // factorial(towers)
        for towers in range(1, n + 1)
    )
    max_pairs = state_count * (state_count - 1)
    if count > max_pairs:
        raise ValueError(
            f"count must be at most {max_pairs} for n={n}"
        )

    problems: list[tuple[BlockState, BlockState]] = []
    seen: set[tuple[BlockState, BlockState]] = set()

    while len(problems) < count:
        problem = (generate_state(n, rng), generate_state(n, rng))

        if problem[0] == problem[1] or problem in seen:
            continue

        seen.add(problem)
        problems.append(problem)

    return problems


def generate_dataset(
    output_dir: str | Path,
    seed: int,
    count_per_n: int,
    min_blocks: int,
    max_blocks: int,
    variant: Variant,
) -> list[Path]:
    if count_per_n < 1:
        raise ValueError("count_per_n must be positive")
    if min_blocks < 3:
        raise ValueError("min_blocks must be at least 3")
    if max_blocks < min_blocks:
        raise ValueError("max_blocks must not be smaller than min_blocks")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    written: list[Path] = []

    for n in range(min_blocks, max_blocks + 1):
        for index, (start, goal) in enumerate(
            generate_problems(n, count_per_n, rng),
            start=1,
        ):
            path = output_dir / f"problem_n{n:02d}_{index:02d}.txt"
            write_problem(path, BlocksProblem(start, goal, variant))
            written.append(path)

    return written
