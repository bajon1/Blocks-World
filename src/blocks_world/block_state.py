from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class BlockState:
    state: tuple[int, ...]

    def __len__(self):
        return len(self.state)

    def get_top_blocks(self) -> list[int]:
        state_set = set(self.state)

        return [
            block
            for block in range(1, len(self.state) + 1)
            if block not in state_set
        ]