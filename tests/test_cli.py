from pathlib import Path

import pytest

from blocks_world.cli import generate_main, problem_main, solve_main
from blocks_world.problem import SearchResult


def test_generate_main_writes_requested_dataset(capsys):
    path = Path("tests/_runtime_generated.txt")

    try:
        exit_code = generate_main(
            [
                "--output",
                str(path),
                "--seed",
                "42",
                "--count",
                "1",
                "--min-blocks",
                "3",
                "--max-blocks",
                "3",
            ]
        )

        assert exit_code == 0
        assert path.exists()
        assert "Generated 1 problems" in capsys.readouterr().out
    finally:
        path.unlink(missing_ok=True)


def test_generate_main_rejects_block_counts_below_project_range():
    with pytest.raises(SystemExit):
        generate_main(["--min-blocks", "2", "--max-blocks", "3"])


def test_problem_main_prints_parsed_problem(capsys):
    exit_code = problem_main(["data/data_manual.txt", "basic"])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "BlockState(state=(0, 1, 0, 2, 3))" in output
    assert "BlockState(state=(2, 3, 4, 5, 0))" in output


def test_cli_help_uses_variant_values(capsys):
    with pytest.raises(SystemExit):
        problem_main(["--help"])

    assert "{basic,extended}" in capsys.readouterr().out


def test_solve_main_runs_configured_solver_and_verifies(capsys):
    path = Path("tests/_runtime_solve.txt")
    path.write_text("0 0\n0 0\n", encoding="utf-8")
    received = []

    def loader(algorithm, max_expanded, heuristic):
        received.append((algorithm, max_expanded, heuristic))

        def solver(_problem):
            return SearchResult(moves=[], visited=4, is_solved=True)

        return solver

    try:
        exit_code = solve_main(
            [str(path), "basic", "dfs", "--max-expanded", "123"],
            solver_loader=loader,
        )
    finally:
        path.unlink(missing_ok=True)

    assert exit_code == 0
    assert received == [("dfs", 123, None)]
    output = capsys.readouterr().out
    assert "status: solved" in output
    assert "verification: passed" in output


def test_solve_main_returns_two_when_solver_hits_limit():
    path = Path("tests/_runtime_solve.txt")
    path.write_text("0 0\n0 1\n", encoding="utf-8")

    def loader(_algorithm, _max_expanded, _heuristic):
        def solver(_problem):
            return SearchResult(moves=[], visited=10, is_solved=False)

        return solver

    try:
        exit_code = solve_main(
            [str(path), "extended", "bfs"],
            solver_loader=loader,
        )
    finally:
        path.unlink(missing_ok=True)

    assert exit_code == 2


def test_solve_main_runs_real_bfs_and_prints_all_metrics(capsys):
    exit_code = solve_main(
        [
            "data/data_manual.txt",
            "extended",
            "bfs",
            "--max-expanded",
            "100000",
        ]
    )

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "length: 5" in output
    assert "peak stored states:" in output
    assert "verification: passed" in output


def test_solve_main_reports_unknown_ida_heuristic(capsys):
    exit_code = solve_main(
        [
            "data/data_manual.txt",
            "extended",
            "ida_star",
            "--heuristic",
            "missing",
        ]
    )

    assert exit_code == 1
    assert "Unknown heuristic" in capsys.readouterr().err
