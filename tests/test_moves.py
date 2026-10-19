import pytest

from blocks_world.block_state import BlockState
from blocks_world.moves import Move, generate_moves, apply_move
from blocks_world.problem import Variant


@pytest.mark.parametrize(
    "variant",
    [Variant.BASIC, Variant.EXTENDED],
)
def test_all_blocks_on_table(variant):
    state = BlockState((0, 0, 0))

    expected = {
        Move(1, 2),
        Move(1, 3),
        Move(2, 1),
        Move(2, 3),
        Move(3, 1),
        Move(3, 2),
    }

    assert set(generate_moves(state, variant)) == expected


@pytest.mark.parametrize(
    "variant",
    [Variant.BASIC, Variant.EXTENDED],
)
def test_single_stack(variant):
    state = BlockState((0, 1, 2))

    assert generate_moves(state, variant) == [Move(3, 0)]


def test_two_stacks_basic():
    state = BlockState((0, 1, 0, 2, 3))

    expected = {
        Move(4, 0),
        Move(5, 0),
    }

    assert set(generate_moves(state, Variant.BASIC)) == expected


def test_two_stacks_extended():
    state = BlockState((0, 1, 0, 2, 3))

    expected = {
        Move(4, 0),
        Move(5, 0),
        Move(4, 5),
        Move(5, 4),
    }

    assert set(generate_moves(state, Variant.EXTENDED)) == expected


def test_basic_move_from_table():
    state = BlockState((0, 1, 0))

    moves = generate_moves(state, Variant.BASIC)

    assert Move(3, 2) in moves
    assert Move(2, 3) not in moves


def test_extended_move_between_stacks():
    state = BlockState((0, 1, 0, 3))

    moves = generate_moves(state, Variant.EXTENDED)

    assert Move(2, 4) in moves
    assert Move(4, 2) in moves


def test_apply_move_to_table():
    state = BlockState((0, 1, 2))

    result = apply_move(state, Move(3, 0))

    assert result == BlockState((0, 1, 0))


def test_apply_move_to_block():
    state = BlockState((0, 0, 0))

    result = apply_move(state, Move(3, 1))

    assert result == BlockState((0, 0, 1))


def test_apply_move_between_stacks():
    state = BlockState((0, 1, 0, 2, 3))

    result = apply_move(state, Move(4, 5))

    assert result == BlockState((0, 1, 0, 5, 3))


def test_apply_move_immutable():
    state = BlockState((0, 1, 2))

    apply_move(state, Move(3, 0))

    assert state == BlockState((0, 1, 2))


@pytest.mark.parametrize(
    "variant",
    [Variant.BASIC, Variant.EXTENDED],
)
def test_no_duplicate_moves(variant):
    state = BlockState((0, 1, 0, 2, 3))

    moves = generate_moves(state, variant)

    assert len(moves) == len(set(moves))


@pytest.mark.parametrize(
    "variant",
    [Variant.BASIC, Variant.EXTENDED],
)
def test_no_self_moves(variant):
    state = BlockState((0, 0, 0, 0))

    moves = generate_moves(state, variant)

    assert all(
        move.block != move.destination
        for move in moves
    )


@pytest.mark.parametrize(
    "state",
    [
        BlockState((0, 0, 0)),
        BlockState((0, 1, 2)),
        BlockState((0, 1, 0, 2, 3)),
        BlockState((0, 0, 2, 3)),
    ],
)
def test_basic_moves_subset_of_extended(state):
    basic = set(generate_moves(state, Variant.BASIC))
    extended = set(generate_moves(state, Variant.EXTENDED))

    assert basic <= extended


def test_move_order_is_deterministic_and_table_first():
    state = BlockState((0, 1, 0, 2, 3))

    assert generate_moves(state, Variant.EXTENDED) == [
        Move(4, 0),
        Move(5, 0),
        Move(4, 5),
        Move(5, 4),
    ]


@pytest.mark.parametrize(
    "variant",
    [Variant.BASIC, Variant.EXTENDED],
)
def test_generated_moves_produce_valid_states(variant):
    state = BlockState((0, 1, 0, 2, 3))

    for move in generate_moves(state, variant):
        result = apply_move(state, move)

        supports = [
            support
            for support in result.state
            if support != 0
        ]

        assert len(supports) == len(set(supports))

        assert all(
            support != block
            for block, support in enumerate(result.state, start=1)
        )

        for block in range(1, len(result) + 1):
            seen = set()
            current = block

            while current != 0:
                assert current not in seen
                seen.add(current)

                assert 1 <= current <= len(result)
                current = result.state[current - 1]
