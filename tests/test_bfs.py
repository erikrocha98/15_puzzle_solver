"""
Testes para a busca BFS.

Cobertura:
  - 8-puzzle (3×3): casos com solução conhecida (0, 1, 2, 4 movimentos)
  - 8-puzzle: limite de nós → retorna None
  - 15-puzzle (4×4): casos fáceis gerados por movimentos a partir do objetivo
  - Métricas: nodes_expanded, solution_length, elapsed_time coerentes
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from puzzle.search.bfs import bfs
from puzzle.state import GOAL_STATE, get_neighbors

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

GOAL_8 = (1, 2, 3, 4, 5, 6, 7, 8, 0)


def apply_moves(goal, moves):
    """Gera estado aplicando sequência de trocas de blank a partir do objetivo."""
    state = list(goal)
    blank = state.index(0)
    for target in moves:
        state[blank], state[target] = state[target], state[blank]
        blank = target
    return tuple(state)


# ---------------------------------------------------------------------------
# 8-puzzle — correção do BFS
# ---------------------------------------------------------------------------

def test_8_goal_state():
    result = bfs(GOAL_8, goal_state=GOAL_8, size=3)
    assert result["solution"] == [GOAL_8]
    assert result["nodes_expanded"] == 0
    assert result["solution_length"] == 0
    print("8-puzzle: estado objetivo OK")


def test_8_one_move():
    state = apply_moves(GOAL_8, [7])
    result = bfs(state, goal_state=GOAL_8, size=3)
    assert result["solution"] is not None
    assert result["solution_length"] == 1
    assert result["solution"][0] == state
    assert result["solution"][-1] == GOAL_8
    print("8-puzzle: 1 movimento OK")


def test_8_two_moves():
    state = apply_moves(GOAL_8, [7, 6])
    result = bfs(state, goal_state=GOAL_8, size=3)
    assert result["solution"] is not None
    assert result["solution_length"] == 2
    print("8-puzzle: 2 movimentos OK")


def test_8_four_moves():
    state = apply_moves(GOAL_8, [7, 4, 5, 8])
    result = bfs(state, goal_state=GOAL_8, size=3)
    assert result["solution"] is not None
    assert result["solution_length"] == 4
    print("8-puzzle: 4 movimentos OK")


def test_8_path_is_connected():
    state = apply_moves(GOAL_8, [7, 4, 3, 4, 7])
    result = bfs(state, goal_state=GOAL_8, size=3)
    assert result["solution"] is not None
    path = result["solution"]
    for i in range(len(path) - 1):
        assert path[i + 1] in get_neighbors(path[i], size=3), \
            f"Estados consecutivos não são vizinhos: {path[i]} → {path[i+1]}"
    print("8-puzzle: caminho conectado OK")


def test_8_max_nodes_returns_none():
    # Estado a 4 movimentos; com max_nodes=2 BFS não chega até a solução
    state = apply_moves(GOAL_8, [7, 4, 5, 8])
    result = bfs(state, goal_state=GOAL_8, size=3, max_nodes=2)
    assert result["solution"] is None
    assert result["nodes_expanded"] >= 1
    print("8-puzzle: limite de nós → None OK")


def test_8_metrics_present():
    state = apply_moves(GOAL_8, [7, 4])
    result = bfs(state, goal_state=GOAL_8, size=3)
    assert result["nodes_expanded"] >= result["solution_length"]
    assert result["elapsed_time"] >= 0.0
    print("8-puzzle: métricas coerentes OK")


# ---------------------------------------------------------------------------
# 15-puzzle — casos fáceis
# ---------------------------------------------------------------------------

def test_15_goal_state():
    result = bfs(GOAL_STATE)
    assert result["solution_length"] == 0
    assert result["nodes_expanded"] == 0
    print("15-puzzle: estado objetivo OK")


def test_15_one_move():
    state = apply_moves(GOAL_STATE, [14])
    result = bfs(state)
    assert result["solution_length"] == 1
    print("15-puzzle: 1 movimento OK")


def test_15_two_moves():
    state = apply_moves(GOAL_STATE, [14, 13])
    result = bfs(state)
    assert result["solution_length"] == 2
    print("15-puzzle: 2 movimentos OK")


def test_15_five_moves():
    state = apply_moves(GOAL_STATE, [14, 10, 9, 8, 4])
    result = bfs(state)
    assert result["solution"] is not None
    assert result["solution_length"] == 5
    print("15-puzzle: 5 movimentos OK")


def test_15_path_connected():
    # Movimentos válidos (adjacentes): 15→14→13→12→8
    state = apply_moves(GOAL_STATE, [14, 13, 12, 8])
    result = bfs(state)
    assert result["solution"] is not None
    path = result["solution"]
    for i in range(len(path) - 1):
        assert path[i + 1] in get_neighbors(path[i]), \
            f"Estados consecutivos não são vizinhos: {path[i]} → {path[i+1]}"
    print("15-puzzle: caminho conectado OK")


def test_15_nodes_grow_with_depth():
    s1 = apply_moves(GOAL_STATE, [14])
    s3 = apply_moves(GOAL_STATE, [14, 10, 9])
    r1 = bfs(s1)
    r3 = bfs(s3)
    assert r3["nodes_expanded"] >= r1["nodes_expanded"]
    print("15-puzzle: nós expandidos crescem com profundidade OK")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 50)
    print("Testes de BFS — 8-puzzle")
    print("=" * 50)
    test_8_goal_state()
    test_8_one_move()
    test_8_two_moves()
    test_8_four_moves()
    test_8_path_is_connected()
    test_8_max_nodes_returns_none()
    test_8_metrics_present()
    print()
    print("=" * 50)
    print("Testes de BFS — 15-puzzle (casos fáceis)")
    print("=" * 50)
    test_15_goal_state()
    test_15_one_move()
    test_15_two_moves()
    test_15_five_moves()
    test_15_path_connected()
    test_15_nodes_grow_with_depth()
    print("=" * 50)
    print("Todos os testes passaram!")
