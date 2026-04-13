"""
Busca em Profundidade (DFS) para o n-puzzle.

Propriedades:
  - Completo (com limite de profundidade e controle de ciclos no caminho).
  - Não-ótimo: a solução encontrada pode ter mais movimentos que o mínimo.
  - Complexidade de tempo: O(b^m), onde m é o limite de profundidade.
  - Complexidade de espaço: O(b*m) — vantagem sobre BFS em memória.

Controle de ciclos
------------------
Utiliza um conjunto de estados no caminho atual (path_set) para evitar
revisitar um mesmo estado dentro de um único ramo de busca. Estados
visitados em ramos distintos podem ser revisitados — esse é o comportamento
esperado do DFS com controle de ciclos por caminho (e não global).

Parâmetros relevantes
---------------------
initial_state : tuple
    Estado inicial (sequência linear de inteiros, 0 = espaço vazio).
goal_state : tuple
    Estado objetivo. Padrão: GOAL_STATE do 15-puzzle.
max_depth : int
    Profundidade máxima de busca. Estados além deste limite não são expandidos.
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

import time

from puzzle.state import get_neighbors, GOAL_STATE, SIZE


def dfs(
    initial_state: tuple,
    goal_state: tuple = GOAL_STATE,
    max_depth: int = 50,
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

    # Cada entrada da pilha: (state, path_como_tupla)
    # path inclui o próprio state; path_set é derivado de path para O(1) lookup.
    stack: list[tuple] = [(initial_state, (initial_state,))]
    nodes_expanded = 0

    while stack:
        if nodes_expanded >= max_nodes:
            break

        state, path = stack.pop()
        nodes_expanded += 1
        depth = len(path) - 1

        if depth >= max_depth:
            continue

        path_set = set(path)  # conjunto dos estados no caminho atual

        for neighbor in get_neighbors(state, size=size):
            if neighbor in path_set:
                continue  # evita ciclo no caminho atual
            if neighbor == goal_state:
                solution = list(path) + [neighbor]
                return {
                    "solution": solution,
                    "nodes_expanded": nodes_expanded,
                    "solution_length": len(solution) - 1,
                    "elapsed_time": time.perf_counter() - start,
                }
            stack.append((neighbor, path + (neighbor,)))

    return {
        "solution": None,
        "nodes_expanded": nodes_expanded,
        "solution_length": None,
        "elapsed_time": time.perf_counter() - start,
    }
