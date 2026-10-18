import pytest

from dataclasses import FrozenInstanceError

from blocks_world.block_state import BlockState, validate_state


def test_state_creation():
    state = BlockState((0, 1, 0, 2, 3))

    assert state.state == (0, 1, 0, 2, 3)


def test_state_length():
    state = BlockState((0, 1, 0, 2, 3))

    assert len(state) == 5


def test_state_equality():
    state1 = BlockState((0, 1, 0))
    state2 = BlockState((0, 1, 0))

    assert state1 == state2


def test_state_inequality():
    state1 = BlockState((0, 1, 0))
    state2 = BlockState((0, 0, 1))

    assert state1 != state2


def test_state_hash():
    state1 = BlockState((0, 1, 0))
    state2 = BlockState((0, 1, 0))

    visited = {state1}

    assert state2 in visited


def test_state_immutable():
    state = BlockState((0, 1, 0))

    with pytest.raises(FrozenInstanceError):
        state.state = (0, 0, 0)


def test_state_slots():
    state = BlockState((0, 1, 0))

    assert not hasattr(state, "__dict__")


# State validation - valid states

@pytest.mark.parametrize(
    "supports",
    [
        (0,),
        (0, 0, 0),
        (0, 1, 2),
        (0, 1, 0, 2, 3),
        (2, 3, 4, 5, 0),
        (0, 0, 2, 3),
        (0, 1, 0, 3, 4),
    ],
)
def test_validate_state_valid(supports):
    assert validate_state(BlockState(supports)) is None


# State validation - invalid states

@pytest.mark.parametrize(
    "supports",
    [
        (1, 0, 0),
        (4, 0, 0),
        (0, -1, 0),
        (0, 1, 1),
        (2, 1, 0),
        (2, 3, 1),
        (0, 3, 2),
        (0, 1, 4, 3),
        (0, 1, 2, 5, 4),
        (0, True, 0),
    ],
)
def test_validate_state_invalid(supports):
    with pytest.raises(ValueError):
        validate_state(BlockState(supports))


@pytest.mark.parametrize(
    "supports, error",
    [
        ((1, 0, 0), "on itself"),
        ((4, 0, 0), "Invalid support"),
        ((0, 1, 1), "Multiple blocks"),
        ((2, 1, 0), "Cycle"),
        ((0, True, 0), "Invalid support type"),
    ],
)
def test_validate_state_error_messages(supports, error):
    with pytest.raises(ValueError, match=error):
        validate_state(BlockState(supports))