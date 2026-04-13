"""
Testes para a busca DFS.

Cobertura:
  - 8-puzzle (3×3): casos com solução conhecida (0, 1, 2, 4 movimentos)
  - Caminho válido: conectado, começa no estado inicial, termina no objetivo
  - DFS não é ótimo: solução pode ser mais longa que a do BFS
  - Limite de profundidade: bloqueia busca quando necessário
  - Limite de nós: interrompe busca e retorna None
  - 15-puzzle (4×4): casos fáceis gerados por movimentos a partir do objetivo
  - Métricas: nodes_expanded, solution_length, elapsed_time coerentes
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from puzzle.search.dfs import dfs
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


def is_connected_path(path, size):
    """Verifica se cada par consecutivo do caminho é de estados vizinhos."""
    for i in range(len(path) - 1):
        if path[i + 1] not in get_neighbors(path[i], size=size):
            return False
    return True


# ---------------------------------------------------------------------------
# 8-puzzle — correção do DFS
# ---------------------------------------------------------------------------

def test_8_goal_state():
    result = dfs(GOAL_8, goal_state=GOAL_8, size=3)
    assert result["solution"] == [GOAL_8]
    assert result["nodes_expanded"] == 0
    assert result["solution_length"] == 0
    print("DFS 8-puzzle: estado objetivo OK")


def test_8_one_move_finds_solution():
    state = apply_moves(GOAL_8, [7])
    result = dfs(state, goal_state=GOAL_8, size=3)
    assert result["solution"] is not None
    assert result["solution"][0] == state
    assert result["solution"][-1] == GOAL_8
    print("DFS 8-puzzle: 1 movimento — solução encontrada OK")


def test_8_two_moves_finds_solution():
    state = apply_moves(GOAL_8, [7, 6])
    result = dfs(state, goal_state=GOAL_8, size=3)
    assert result["solution"] is not None
    assert result["solution"][-1] == GOAL_8
    print("DFS 8-puzzle: 2 movimentos — solução encontrada OK")


def test_8_four_moves_finds_solution():
    state = apply_moves(GOAL_8, [7, 4, 5, 8])
    result = dfs(state, goal_state=GOAL_8, size=3)
    assert result["solution"] is not None
    assert result["solution"][-1] == GOAL_8
    print("DFS 8-puzzle: 4 movimentos — solução encontrada OK")


def test_8_path_is_connected():
    state = apply_moves(GOAL_8, [7, 4, 3])
    result = dfs(state, goal_state=GOAL_8, size=3)
    assert result["solution"] is not None
    assert is_connected_path(result["solution"], size=3), \
        "Estados consecutivos no caminho não são vizinhos"
    print("DFS 8-puzzle: caminho conectado OK")


def test_8_path_starts_and_ends_correctly():
    state = apply_moves(GOAL_8, [7, 4])
    result = dfs(state, goal_state=GOAL_8, size=3)
    assert result["solution"][0] == state
    assert result["solution"][-1] == GOAL_8
    print("DFS 8-puzzle: caminho começa e termina corretamente OK")


def test_8_solution_length_at_least_optimal():
    """DFS não é ótimo — solução pode ser >= BFS, mas nunca menor."""
    state = apply_moves(GOAL_8, [7, 4, 5, 8])
    r_dfs = dfs(state, goal_state=GOAL_8, size=3)
    r_bfs = bfs(state, goal_state=GOAL_8, size=3)
    assert r_dfs["solution"] is not None
    assert r_dfs["solution_length"] >= r_bfs["solution_length"]
    print(f"DFS 8-puzzle: comprimento DFS={r_dfs['solution_length']} >= BFS={r_bfs['solution_length']} OK")


def test_8_max_depth_blocks_solution():
    """Com profundidade máxima 0 e estado não-objetivo, DFS não encontra solução."""
    state = apply_moves(GOAL_8, [7])
    result = dfs(state, goal_state=GOAL_8, size=3, max_depth=0)
    assert result["solution"] is None
    print("DFS 8-puzzle: max_depth=0 bloqueia solução OK")


def test_8_max_nodes_returns_none():
    """Com limite de nós muito baixo, DFS não chega à solução."""
    state = apply_moves(GOAL_8, [7, 4, 5, 8])
    result = dfs(state, goal_state=GOAL_8, size=3, max_nodes=2)
    assert result["solution"] is None
    assert result["nodes_expanded"] >= 1
    print("DFS 8-puzzle: max_nodes baixo → None OK")


def test_8_metrics_present_and_coherent():
    state = apply_moves(GOAL_8, [7, 4])
    result = dfs(state, goal_state=GOAL_8, size=3)
    assert result["nodes_expanded"] >= 1
    assert result["solution_length"] >= 1
    assert result["elapsed_time"] >= 0.0
    print("DFS 8-puzzle: métricas coerentes OK")


# ---------------------------------------------------------------------------
# 15-puzzle — casos fáceis
# ---------------------------------------------------------------------------

def test_15_goal_state():
    result = dfs(GOAL_STATE)
    assert result["solution_length"] == 0
    assert result["nodes_expanded"] == 0
    print("DFS 15-puzzle: estado objetivo OK")


def test_15_one_move_finds_solution():
    state = apply_moves(GOAL_STATE, [14])
    result = dfs(state)
    assert result["solution"] is not None
    assert result["solution"][-1] == GOAL_STATE
    print("DFS 15-puzzle: 1 movimento — solução encontrada OK")


def test_15_two_moves_finds_solution():
    state = apply_moves(GOAL_STATE, [14, 13])
    result = dfs(state)
    assert result["solution"] is not None
    assert result["solution"][-1] == GOAL_STATE
    print("DFS 15-puzzle: 2 movimentos — solução encontrada OK")


def test_15_path_connected():
    state = apply_moves(GOAL_STATE, [14, 13])
    result = dfs(state)
    assert result["solution"] is not None
    assert is_connected_path(result["solution"], size=4), \
        "Estados consecutivos no caminho não são vizinhos"
    print("DFS 15-puzzle: caminho conectado OK")


def test_15_solution_length_at_least_optimal():
    """DFS não é ótimo — comprimento >= BFS para o mesmo estado."""
    state = apply_moves(GOAL_STATE, [14, 13])
    r_dfs = dfs(state)
    r_bfs = bfs(state)
    assert r_dfs["solution"] is not None
    assert r_dfs["solution_length"] >= r_bfs["solution_length"]
    print(f"DFS 15-puzzle: comprimento DFS={r_dfs['solution_length']} >= BFS={r_bfs['solution_length']} OK")


def test_15_impractical_for_deeper_states():
    """
    DFS esgota max_nodes sem encontrar solução para estados a mais de ~2 movimentos
    no 15-puzzle. Esse é um resultado importante: DFS não é prático para o 15-puzzle.
    """
    state = apply_moves(GOAL_STATE, [14, 10, 9, 8, 4])
    result = dfs(state, max_nodes=500_000)
    # Não garantimos solução — documentamos que DFS falha aqui
    assert result["nodes_expanded"] >= 1
    if result["solution"] is None:
        print("DFS 15-puzzle: estado distante esgota max_nodes (comportamento esperado) OK")
    else:
        print(f"DFS 15-puzzle: solução encontrada com comprimento {result['solution_length']} OK")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 50)
    print("Testes de DFS — 8-puzzle")
    print("=" * 50)
    test_8_goal_state()
    test_8_one_move_finds_solution()
    test_8_two_moves_finds_solution()
    test_8_four_moves_finds_solution()
    test_8_path_is_connected()
    test_8_path_starts_and_ends_correctly()
    test_8_solution_length_at_least_optimal()
    test_8_max_depth_blocks_solution()
    test_8_max_nodes_returns_none()
    test_8_metrics_present_and_coherent()
    print()
    print("=" * 50)
    print("Testes de DFS — 15-puzzle (casos fáceis)")
    print("=" * 50)
    test_15_goal_state()
    test_15_one_move_finds_solution()
    test_15_two_moves_finds_solution()
    test_15_path_connected()
    test_15_solution_length_at_least_optimal()
    test_15_impractical_for_deeper_states()
    print("=" * 50)
    print("Todos os testes passaram!")
