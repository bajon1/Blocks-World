"""Tests for the search solvers.

All solvers share one call convention:
    solver(problem, node_limit=..., stats=None) -> SearchResult(moves, n_moves)
and raise NodeLimitExceeded when the node limit is exceeded.

Solutions are verified independently of the verifier module, using only
generate_moves and apply_move.
"""
import random
from dataclasses import fields
from itertools import product

import pytest

from blocks_world.block_state import BlockState, validate_state
from blocks_world.generator import generate_problems
from blocks_world.moves import Move, apply_move, generate_moves
from blocks_world.problem import BlocksProblem, SearchResult, Variant
from blocks_world.solvers.common import NodeLimitExceeded, SearchStats
from blocks_world.solvers.dfs import dfs

SOLVERS = {"dfs": dfs}

VARIANTS = [Variant.BASIC, Variant.EXTENDED]

# Example from the project description: the shortest solution has 7 moves
# in the basic variant and 5 moves in the extended variant.
SPEC_START = BlockState((0, 1, 0, 2, 3))
SPEC_GOAL = BlockState((2, 3, 4, 5, 0))
SPEC_OPTIMAL = {Variant.BASIC: 7, Variant.EXTENDED: 5}


def assert_valid_solution(problem, result):
    """Check that every move is legal in the problem's variant and the final state is the goal."""
    assert isinstance(result, SearchResult)
    assert isinstance(result.moves, list)
    assert result.n_moves == len(result.moves)

    state = problem.start
    for number, move in enumerate(result.moves, start=1):
        assert isinstance(move, Move)
        assert move in generate_moves(state, problem.variant), (
            f"move {number} {move} is not allowed in the {problem.variant.value} variant"
        )
        state = apply_move(state, move)

    assert state == problem.goal


def all_states(n):
    """Return every valid state of n blocks."""
    states = []
    for supports in product(range(n + 1), repeat=n):
        try:
            validate_state(BlockState(supports))
        except ValueError:
            continue
        states.append(BlockState(supports))
    return states


def random_problems(n, variant, seed=42, count=5):
    """Return `count` reproducible random problems with n blocks."""
    rng = random.Random(seed)
    return [
        BlocksProblem(start, goal, variant)
        for start, goal in generate_problems(n, count, rng)
    ]


solvers = pytest.mark.parametrize("solver", SOLVERS.values(), ids=SOLVERS.keys())
variants = pytest.mark.parametrize("variant", VARIANTS)


def test_search_result_has_only_moves_and_n_moves():
    assert [f.name for f in fields(SearchResult)] == ["moves", "n_moves"]


@solvers
@variants
def test_spec_example(solver, variant):
    problem = BlocksProblem(SPEC_START, SPEC_GOAL, variant)

    result = solver(problem)

    assert_valid_solution(problem, result)
    # No solution can be shorter than the optimal one.
    assert result.n_moves >= SPEC_OPTIMAL[variant]


@solvers
@variants
def test_start_equals_goal(solver, variant):
    problem = BlocksProblem(SPEC_START, SPEC_START, variant)

    result = solver(problem)

    assert result.moves == []
    assert result.n_moves == 0


@solvers
@variants
def test_goal_one_move_away_is_found_with_node_limit_1(solver, variant):
    problem = BlocksProblem(BlockState((0, 1, 2)), BlockState((0, 1, 0)), variant)

    result = solver(problem, node_limit=1)

    assert_valid_solution(problem, result)
    assert result.moves == [Move(3, 0)]


@solvers
@variants
def test_node_limit_exceeded_is_raised(solver, variant):
    # The specification example needs at least 5 moves, so one expanded node is not enough.
    problem = BlocksProblem(SPEC_START, SPEC_GOAL, variant)
    stats = SearchStats()

    with pytest.raises(NodeLimitExceeded):
        solver(problem, node_limit=1, stats=stats)

    assert 0 < stats.expanded <= 1


@solvers
@variants
def test_stats_are_filled(solver, variant):
    problem = BlocksProblem(SPEC_START, SPEC_GOAL, variant)
    stats = SearchStats()

    result = solver(problem, node_limit=100_000, stats=stats)

    assert_valid_solution(problem, result)
    assert stats.expanded > 0
    assert stats.max_stored >= result.n_moves


@solvers
@variants
def test_result_is_deterministic(solver, variant):
    problem = random_problems(6, variant)[0]

    first = solver(problem, node_limit=100_000)
    second = solver(problem, node_limit=100_000)

    assert first.moves == second.moves


@solvers
@variants
@pytest.mark.parametrize("n", [3, 4])
def test_every_pair_of_states_is_solvable(solver, variant, n):
    """Exhaustive check: 13 states (169 pairs) for n=3 and 73 states (5329 pairs) for n=4.

    Every state is reachable from every other state in both variants,
    so a solution must always be found.
    """
    states = all_states(n)

    for start in states:
        for goal in states:
            problem = BlocksProblem(start, goal, variant)
            result = solver(problem, node_limit=100_000)
            assert_valid_solution(problem, result)


@variants
def test_dfs_random_problems_n3_to_n6(variant):
    """Five seeded random problems per n. Plain DFS may return long solutions, so only validity is checked."""
    for n in range(3, 7):
        for problem in random_problems(n, variant):
            result = dfs(problem, node_limit=100_000)

            assert_valid_solution(problem, result)


@pytest.mark.skip(reason="requires move ordering in DFS, which the plain variant does not use")
@variants
def test_dfs_with_ordering_handles_large_problems(variant):
    """With move ordering, problems with 10 to 15 blocks are solved within 5000 expanded nodes."""
    for n in range(10, 16):
        for problem in random_problems(n, variant):
            result = dfs(problem, node_limit=5_000)

            assert_valid_solution(problem, result)