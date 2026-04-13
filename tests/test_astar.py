"""
Testes para a busca A* e a heurística de distância de Manhattan.

Cobertura:
  - Heurística: valor correto em casos conhecidos; admissível (≤ solução ótima)
  - 8-puzzle (3×3): estado objetivo, 1/2/4 movimentos, caminho conectado
  - 8-puzzle: limite de nós → retorna None
  - 8-puzzle: A* é ótimo (solution_length == BFS)
  - 15-puzzle: casos fáceis e casos médios (onde BFS/DFS não chegam)
  - Métricas: nodes_expanded, solution_length, elapsed_time coerentes
  - A* expande menos nós que BFS em instâncias com profundidade ≥ 4
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from puzzle.search.astar import astar, manhattan_distance
from puzzle.search.bfs import bfs
from puzzle.state import GOAL_STATE, get_neighbors

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

GOAL_8 = (1, 2, 3, 4, 5, 6, 7, 8, 0)


def apply_moves(goal, moves):
    """Aplica sequência de trocas de blank a partir do objetivo."""
    state = list(goal)
    blank = state.index(0)
    for target in moves:
        state[blank], state[target] = state[target], state[blank]
        blank = target
    return tuple(state)


# ---------------------------------------------------------------------------
# Heurística de Manhattan
# ---------------------------------------------------------------------------

def test_manhattan_goal_is_zero():
    assert manhattan_distance(GOAL_8, GOAL_8, size=3) == 0
    assert manhattan_distance(GOAL_STATE, GOAL_STATE) == 0
    print("Manhattan: estado objetivo = 0 OK")


def test_manhattan_one_move_8puzzle():
    # Blank move: índice 8 → 7. Peça 8 sai de índice 7 para índice 8.
    # Posição objetivo de 8 é índice 7 (linha 2, col 1).
    # Posição atual de 8 é índice 8 (linha 2, col 2) → Manhattan = 1.
    state = apply_moves(GOAL_8, [7])
    assert manhattan_distance(state, GOAL_8, size=3) == 1
    print("Manhattan: 1 movimento = 1 OK")


def test_manhattan_admissible_8puzzle():
    """h(n) ≤ solução ótima para várias instâncias do 8-puzzle."""
    import random
    random.seed(42)
    for _ in range(20):
        # Gera instância a até 10 movimentos do objetivo
        moves = [random.randint(0, 8) for _ in range(10)]
        state = GOAL_8
        blank = state.index(0)
        for m in moves:
            neighbors = get_neighbors(state, size=3)
            if neighbors:
                import random as r
                state = r.choice(neighbors)
        h = manhattan_distance(state, GOAL_8, size=3)
        opt = bfs(state, goal_state=GOAL_8, size=3)
        if opt["solution"] is not None:
            assert h <= opt["solution_length"], \
                f"Heurística {h} > solução ótima {opt['solution_length']}"
    print("Manhattan: admissível para 20 instâncias aleatórias OK")


# ---------------------------------------------------------------------------
# 8-puzzle — correção do A*
# ---------------------------------------------------------------------------

def test_8_goal_state():
    result = astar(GOAL_8, goal_state=GOAL_8, size=3)
    assert result["solution"] == [GOAL_8]
    assert result["nodes_expanded"] == 0
    assert result["solution_length"] == 0
    print("8-puzzle A*: estado objetivo OK")


def test_8_one_move():
    state = apply_moves(GOAL_8, [7])
    result = astar(state, goal_state=GOAL_8, size=3)
    assert result["solution"] is not None
    assert result["solution_length"] == 1
    assert result["solution"][0] == state
    assert result["solution"][-1] == GOAL_8
    print("8-puzzle A*: 1 movimento OK")


def test_8_two_moves():
    state = apply_moves(GOAL_8, [7, 6])
    result = astar(state, goal_state=GOAL_8, size=3)
    assert result["solution"] is not None
    assert result["solution_length"] == 2
    print("8-puzzle A*: 2 movimentos OK")


def test_8_four_moves():
    state = apply_moves(GOAL_8, [7, 4, 5, 8])
    result = astar(state, goal_state=GOAL_8, size=3)
    assert result["solution"] is not None
    assert result["solution_length"] == 4
    print("8-puzzle A*: 4 movimentos OK")


def test_8_path_is_connected():
    state = apply_moves(GOAL_8, [7, 4, 3, 4, 7])
    result = astar(state, goal_state=GOAL_8, size=3)
    assert result["solution"] is not None
    path = result["solution"]
    for i in range(len(path) - 1):
        assert path[i + 1] in get_neighbors(path[i], size=3), \
            f"Estados consecutivos não são vizinhos: {path[i]} → {path[i+1]}"
    print("8-puzzle A*: caminho conectado OK")


def test_8_max_nodes_returns_none():
    state = apply_moves(GOAL_8, [7, 4, 5, 8])
    result = astar(state, goal_state=GOAL_8, size=3, max_nodes=2)
    assert result["solution"] is None
    assert result["nodes_expanded"] >= 1
    print("8-puzzle A*: limite de nós → None OK")


def test_8_optimal_matches_bfs():
    """A* deve encontrar a mesma profundidade ótima que BFS."""
    state = apply_moves(GOAL_8, [7, 4, 3, 6, 7, 8])
    r_astar = astar(state, goal_state=GOAL_8, size=3)
    r_bfs = bfs(state, goal_state=GOAL_8, size=3)
    assert r_astar["solution"] is not None
    assert r_bfs["solution"] is not None
    assert r_astar["solution_length"] == r_bfs["solution_length"], \
        f"A* ({r_astar['solution_length']}) ≠ BFS ({r_bfs['solution_length']})"
    print("8-puzzle A*: ótimo igual ao BFS OK")


def test_8_fewer_nodes_than_bfs():
    """A* deve expandir menos ou igual nós que BFS em instâncias não triviais."""
    # 6 movimentos garante profundidade suficiente para a heurística ajudar
    state = apply_moves(GOAL_8, [7, 4, 3, 6, 7, 8])
    r_astar = astar(state, goal_state=GOAL_8, size=3)
    r_bfs = bfs(state, goal_state=GOAL_8, size=3)
    assert r_astar["nodes_expanded"] <= r_bfs["nodes_expanded"], (
        f"A* ({r_astar['nodes_expanded']}) expandiu mais que BFS "
        f"({r_bfs['nodes_expanded']})"
    )
    print("8-puzzle A*: menos nós que BFS OK")


# ---------------------------------------------------------------------------
# 15-puzzle — casos fáceis
# ---------------------------------------------------------------------------

def test_15_goal_state():
    result = astar(GOAL_STATE)
    assert result["solution_length"] == 0
    assert result["nodes_expanded"] == 0
    print("15-puzzle A*: estado objetivo OK")


def test_15_one_move():
    state = apply_moves(GOAL_STATE, [14])
    result = astar(state)
    assert result["solution_length"] == 1
    print("15-puzzle A*: 1 movimento OK")


def test_15_five_moves():
    state = apply_moves(GOAL_STATE, [14, 10, 9, 8, 4])
    result = astar(state)
    assert result["solution"] is not None
    assert result["solution_length"] == 5
    print("15-puzzle A*: 5 movimentos OK")


def test_15_path_connected():
    state = apply_moves(GOAL_STATE, [14, 13, 12, 8])
    result = astar(state)
    assert result["solution"] is not None
    path = result["solution"]
    for i in range(len(path) - 1):
        assert path[i + 1] in get_neighbors(path[i]), \
            f"Estados consecutivos não são vizinhos"
    print("15-puzzle A*: caminho conectado OK")


def test_15_optimal_matches_bfs():
    """A* deve ser ótimo: mesmo número de movimentos que BFS.

    Sequência de 6 movimentos válidos (blank adjacente a cada alvo):
      15→14 (3,3→3,2), 14→10 (3,2→2,2), 10→9 (2,2→2,1),
       9→5  (2,1→1,1),  5→6  (1,1→1,2),  6→7  (1,2→1,3)
    """
    state = apply_moves(GOAL_STATE, [14, 10, 9, 5, 6, 7])
    r_astar = astar(state)
    r_bfs = bfs(state)
    assert r_astar["solution"] is not None
    assert r_bfs["solution"] is not None
    assert r_astar["solution_length"] == r_bfs["solution_length"]
    print("15-puzzle A*: ótimo igual ao BFS OK")


# ---------------------------------------------------------------------------
# Casos onde BFS/DFS falham mas A* resolve
# ---------------------------------------------------------------------------

def test_15_deep_instance_astar_succeeds():
    """
    Instância a ~20 movimentos do objetivo.
    BFS com max_nodes=500k geralmente falha; A* resolve com muito menos nós.
    """
    # Sequência determinística de 20 movimentos válidos a partir do objetivo
    moves_seq = [14, 13, 12, 8, 4, 0, 1, 2, 3, 7, 11, 10, 9, 13, 14, 15, 11, 7, 6, 5]
    state = apply_moves(GOAL_STATE, moves_seq)

    r_astar = astar(state, max_nodes=500_000)
    r_bfs = bfs(state, max_nodes=500_000)

    assert r_astar["solution"] is not None, "A* deveria resolver esta instância"

    if r_bfs["solution"] is None:
        print(
            f"15-puzzle A* vence BFS: A* resolveu em {r_astar['solution_length']} "
            f"movimentos e {r_astar['nodes_expanded']} nós; "
            f"BFS falhou com {r_bfs['nodes_expanded']} nós expandidos"
        )
    else:
        print(
            f"15-puzzle A* e BFS resolveram: A* {r_astar['nodes_expanded']} nós, "
            f"BFS {r_bfs['nodes_expanded']} nós"
        )


def test_metrics_present():
    state = apply_moves(GOAL_STATE, [14, 10])
    result = astar(state)
    assert result["nodes_expanded"] >= 1
    assert result["elapsed_time"] >= 0.0
    print("15-puzzle A*: métricas presentes OK")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 55)
    print("Heurística de Manhattan")
    print("=" * 55)
    test_manhattan_goal_is_zero()
    test_manhattan_one_move_8puzzle()
    test_manhattan_admissible_8puzzle()

    print()
    print("=" * 55)
    print("Testes de A* — 8-puzzle")
    print("=" * 55)
    test_8_goal_state()
    test_8_one_move()
    test_8_two_moves()
    test_8_four_moves()
    test_8_path_is_connected()
    test_8_max_nodes_returns_none()
    test_8_optimal_matches_bfs()
    test_8_fewer_nodes_than_bfs()

    print()
    print("=" * 55)
    print("Testes de A* — 15-puzzle (casos fáceis)")
    print("=" * 55)
    test_15_goal_state()
    test_15_one_move()
    test_15_five_moves()
    test_15_path_connected()
    test_15_optimal_matches_bfs()

    print()
    print("=" * 55)
    print("A* vs BFS/DFS em instâncias difíceis")
    print("=" * 55)
    test_15_deep_instance_astar_succeeds()
    test_metrics_present()

    print()
    print("=" * 55)
    print("Todos os testes passaram!")
    print("=" * 55)
