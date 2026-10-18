from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class BlockState:
    state: tuple[int, ...]

    def __len__(self):
        return len(self.state)


def validate_state(state: BlockState) -> None:
    supports = state.state
    n = len(supports)

    above = [0] * (n + 1)

    for block, support in enumerate(supports, start=1):
        if not isinstance(support, int) or isinstance(support, bool):
            raise ValueError(f"Invalid support type for block {block}")

        if not 0 <= support <= n:
            raise ValueError(f"Invalid support {support} for block {block}")

        if support == block:
            raise ValueError(f"Block {block} is on itself")

        if support != 0:
            if above[support] != 0:
                raise ValueError(
                    f"Multiple blocks on block {support}"
                )

            above[support] = block

    visited_count = 0

    for block, support in enumerate(supports, start=1):
        if support != 0:
            continue

        current = block

        while current != 0:
            visited_count += 1
            current = above[current]

    if visited_count != n:
        raise ValueError("Cycle")