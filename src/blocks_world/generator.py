import random

from .block_state import BlockState


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

    return [
        (generate_state(n, rng), generate_state(n, rng))
        for _ in range(count)
    ]