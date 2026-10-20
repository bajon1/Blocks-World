from collections import deque
from itertools import product
import tracemalloc

import pytest

from blocks_world.block_state import BlockState, validate_state
from blocks_world.moves import generate_moves, apply_move
from blocks_world.problem import BlocksProblem, Variant
from blocks_world.solvers.bfs import bfs
from blocks_world.solvers.dfs import dfs
from blocks_world.solvers.heuristics import foundation_blocks, misplaced_blocks
from blocks_world.solvers.idastar import ida_star
from blocks_world.verifier import verify_solution


SAMPLE_START = BlockState((0, 1, 0, 2, 3))
SAMPLE_GOAL = BlockState((2, 3, 4, 5, 0))


def problem(variant: Variant) -> BlocksProblem:
    return BlocksProblem(SAMPLE_START, SAMPLE_GOAL, variant)


def exact_distance(start: BlockState, goal: BlockState) -> int:
    queue = deque([(start, 0)])
    seen = {start}
    while queue:
        state, distance = queue.popleft()
        if state == goal:
            return distance
        for move in generate_moves(state, Variant.EXTENDED):
            successor = apply_move(state, move)
            if successor not in seen:
                seen.add(successor)
                queue.append((successor, distance + 1))
    raise AssertionError("Every valid Blocks World state must be reachable")


def valid_states(n: int) -> list[BlockState]:
    states = []
    for supports in product(range(n + 1), repeat=n):
        state = BlockState(supports)
        try:
            validate_state(state)
        except ValueError:
            continue
        states.append(state)
    return states


def test_dfs_finds_a_sequence_that_passes_verification():
    given = problem(Variant.BASIC)
    result = dfs(given, max_expanded=100_000)
    assert result.is_solved
    assert result.visited > 0
    assert verify_solution(given, result) is None


def test_dfs_can_find_child_goal_after_expanding_only_root():
    given = BlocksProblem(
        start=BlockState((0, 1, 2)),
        goal=BlockState((0, 1, 0)),
        variant=Variant.BASIC,
    )

    result = dfs(given, max_expanded=1)

    assert result.is_solved
    assert result.visited == 1
    assert verify_solution(given, result) is None


@pytest.mark.parametrize(
    ("variant", "expected_length"),
    [(Variant.BASIC, 7), (Variant.EXTENDED, 5)],
)
def test_bfs_returns_pdf_sample_shortest_length(variant, expected_length):
    given = problem(variant)
    result = bfs(given, max_expanded=100_000)
    assert result.is_solved
    assert result.n_moves == expected_length
    assert verify_solution(given, result) is None


@pytest.mark.parametrize(
    "heuristic",
    ["misplaced", "foundation"],
)
def test_ida_star_returns_pdf_sample_shortest_length(heuristic):
    given = problem(Variant.EXTENDED)
    result = ida_star(given, max_expanded=100_000, heuristic=heuristic)
    assert result.is_solved
    assert result.n_moves == 5
    assert verify_solution(given, result) is None


@pytest.mark.parametrize("solver", [dfs, bfs])
def test_graph_search_reports_node_limit_without_partial_solution(solver):
    result = solver(problem(Variant.EXTENDED), max_expanded=1)
    assert not result.is_solved
    assert result.moves == []
    assert result.visited == 1


@pytest.mark.parametrize("solver", [dfs, bfs])
def test_graph_search_rejects_nonpositive_limit(solver):
    with pytest.raises(ValueError, match="positive"):
        solver(problem(Variant.BASIC), max_expanded=0)


def test_ida_star_reports_node_limit_across_all_iterations():
    result = ida_star(
        problem(Variant.EXTENDED),
        max_expanded=1,
        heuristic="misplaced",
    )
    assert not result.is_solved
    assert result.moves == []
    assert result.visited == 1


def test_ida_star_rejects_nonpositive_limit():
    with pytest.raises(ValueError, match="positive"):
        ida_star(
            problem(Variant.EXTENDED),
            max_expanded=0,
            heuristic="misplaced",
        )


@pytest.mark.parametrize("solver", [dfs, bfs])
def test_graph_search_handles_already_solved_problem_without_expansion(solver):
    state = BlockState((0, 1, 0))
    given = BlocksProblem(state, state, Variant.BASIC)
    result = solver(given, max_expanded=1)
    assert result.is_solved
    assert result.moves == []
    assert result.visited == 0


def test_ida_star_rejects_unknown_heuristic():
    with pytest.raises(ValueError, match="Unknown heuristic"):
        ida_star(problem(Variant.EXTENDED), max_expanded=10, heuristic="missing")


def test_improved_heuristic_counts_correct_blocks_that_must_be_removed():
    state = BlockState((0, 1, 2))
    goal = BlockState((0, 0, 2))
    assert misplaced_blocks(state, goal) == 1
    assert foundation_blocks(state, goal) == 3
    assert exact_distance(state, goal) == 3


def test_heuristics_are_admissible_for_every_three_block_state():
    goal = BlockState((0, 1, 2))
    for state in valid_states(3):
        distance = exact_distance(state, goal)
        basic = misplaced_blocks(state, goal)
        improved = foundation_blocks(state, goal)
        assert basic <= improved <= distance, state


def test_dfs_limit_does_not_retain_parent_record_for_every_state():
    given = BlocksProblem(
        start=BlockState((9, 14, 13, 6, 3, 11, 0, 15, 10, 12, 0, 0, 7, 0, 0)),
        goal=BlockState((5, 15, 0, 10, 9, 1, 0, 3, 11, 12, 0, 0, 2, 13, 7)),
        variant=Variant.BASIC,
    )
    tracemalloc.start()
    try:
        result = dfs(given, max_expanded=5_000)
        _, peak_bytes = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert result.visited <= 5_000
    if result.is_solved:
        assert verify_solution(given, result) is None
    assert peak_bytes < 50_000_000


def test_ida_star_keeps_iterative_deepening_memory_bounded():
    given = BlocksProblem(
        start=BlockState((9, 14, 13, 6, 3, 11, 0, 15, 10, 12, 0, 0, 7, 0, 0)),
        goal=BlockState((5, 15, 0, 10, 9, 1, 0, 3, 11, 12, 0, 0, 2, 13, 7)),
        variant=Variant.EXTENDED,
    )
    tracemalloc.start()
    try:
        result = ida_star(
            given,
            max_expanded=5_000,
            heuristic="misplaced",
        )
        _, peak_bytes = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert not result.is_solved
    assert result.visited == 5_000
    assert peak_bytes < 12_000_000
