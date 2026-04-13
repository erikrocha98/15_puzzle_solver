"""
Busca em Largura (BFS) para o n-puzzle.

Propriedades:
  - Completo: encontra solução se existir (dentro do limite de nós).
  - Ótimo: garante o menor número de movimentos.
  - Complexidade de tempo e espaço: O(b^d), onde b é o fator de ramificação
    (~2–4 para o puzzle) e d é a profundidade da solução.

Parâmetros relevantes
---------------------
initial_state : tuple
    Estado inicial (sequência linear de inteiros, 0 = espaço vazio).
goal_state : tuple
    Estado objetivo. Padrão: GOAL_STATE do 15-puzzle.
max_nodes : int
    Limite de nós expandidos. Interrompe a busca se excedido.
size : int
    Largura da grade (4 para 15-puzzle, 3 para 8-puzzle).

Retorno
-------
dict com:
  'solution'       : lista de estados do inicial ao objetivo, ou None
  'nodes_expanded' : número de nós expandidos
  'solution_length': número de movimentos (len(solution) - 1), ou None
  'elapsed_time'   : tempo de execução em segundos
"""

from collections import deque
import time

from puzzle.state import get_neighbors, GOAL_STATE, SIZE


def bfs(
    initial_state: tuple,
    goal_state: tuple = GOAL_STATE,
    max_nodes: int = 500_000,
    size: int = SIZE,
) -> dict:
    start = time.perf_counter()

    if initial_state == goal_state:
        return {
            "solution": [initial_state],
            "nodes_expanded": 0,
            "solution_length": 0,
            "elapsed_time": 0.0,
        }

    # parent[state] = estado anterior no caminho (None para o estado inicial)
    parent: dict[tuple, tuple | None] = {initial_state: None}
    queue: deque[tuple] = deque([initial_state])
    nodes_expanded = 0

    while queue:
        if nodes_expanded >= max_nodes:
            break

        state = queue.popleft()
        nodes_expanded += 1

        for neighbor in get_neighbors(state, size=size):
            if neighbor in parent:
                continue
            parent[neighbor] = state
            if neighbor == goal_state:
                path = _reconstruct_path(parent, neighbor)
                return {
                    "solution": path,
                    "nodes_expanded": nodes_expanded,
                    "solution_length": len(path) - 1,
                    "elapsed_time": time.perf_counter() - start,
                }
            queue.append(neighbor)

    return {
        "solution": None,
        "nodes_expanded": nodes_expanded,
        "solution_length": None,
        "elapsed_time": time.perf_counter() - start,
    }


def _reconstruct_path(parent: dict, goal: tuple) -> list[tuple]:
    path: list[tuple] = []
    state: tuple | None = goal
    while state is not None:
        path.append(state)
        state = parent[state]
    path.reverse()
    return path
