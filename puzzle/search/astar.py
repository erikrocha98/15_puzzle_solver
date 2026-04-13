"""
Busca A* para o n-puzzle.

Propriedades:
  - Completo: encontra solução se existir.
  - Ótimo: garante o menor número de movimentos quando h(n) é admissível.
  - Complexidade de tempo e espaço: exponencial no pior caso, mas muito
    melhor que BFS/DFS na prática com uma boa heurística.

Função de custo
---------------
  g(n) = profundidade do nó n (número de movimentos desde o estado inicial).

Heurística
----------
  h(n) = distância de Manhattan: para cada peça (exceto o espaço vazio),
  soma-se |linha_atual - linha_objetivo| + |coluna_atual - coluna_objetivo|.
  Essa heurística é admissível (nunca superestima) e consistente, portanto
  A* com ela é ótimo e completo.

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

import heapq
import time

from puzzle.state import get_neighbors, GOAL_STATE, SIZE


def manhattan_distance(state: tuple, goal_state: tuple, size: int = SIZE) -> int:
    """
    Calcula a distância de Manhattan total entre o estado atual e o objetivo.
    O espaço vazio (0) é ignorado.
    """
    distance = 0
    # Pré-computa posição objetivo de cada peça
    goal_pos = {tile: divmod(i, size) for i, tile in enumerate(goal_state)}
    for i, tile in enumerate(state):
        if tile == 0:
            continue
        row, col = divmod(i, size)
        goal_row, goal_col = goal_pos[tile]
        distance += abs(row - goal_row) + abs(col - goal_col)
    return distance


def astar(
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

    h0 = manhattan_distance(initial_state, goal_state, size)

    # Heap: (f, g, counter, state)
    # counter desempata quando f e g são iguais, evitando comparação de tuplas de estado
    counter = 0
    heap: list = [(h0, 0, counter, initial_state)]

    # g_score[state] = menor custo conhecido (profundidade) até state
    g_score: dict[tuple, int] = {initial_state: 0}

    # parent[state] = estado anterior no caminho ótimo
    parent: dict[tuple, tuple | None] = {initial_state: None}

    nodes_expanded = 0

    while heap:
        if nodes_expanded >= max_nodes:
            break

        f, g, _, state = heapq.heappop(heap)

        # Nó desatualizado: já foi expandido com custo menor
        if g > g_score.get(state, float("inf")):
            continue

        nodes_expanded += 1

        if state == goal_state:
            path = _reconstruct_path(parent, state)
            return {
                "solution": path,
                "nodes_expanded": nodes_expanded,
                "solution_length": len(path) - 1,
                "elapsed_time": time.perf_counter() - start,
            }

        for neighbor in get_neighbors(state, size=size):
            tentative_g = g + 1  # custo unitário por movimento
            if tentative_g < g_score.get(neighbor, float("inf")):
                g_score[neighbor] = tentative_g
                parent[neighbor] = state
                h = manhattan_distance(neighbor, goal_state, size)
                counter += 1
                heapq.heappush(heap, (tentative_g + h, tentative_g, counter, neighbor))

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
