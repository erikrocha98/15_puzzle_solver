"""
Geração de instâncias de dificuldade controlada para o benchmark.

Estratégia: caminhada aleatória a partir do estado objetivo.
A cada passo, sorteia um vizinho diferente do estado anterior (evita
reverter imediatamente o último movimento). Isso produz instâncias com
profundidade mínima ≤ N, mas cujo custo real cresce com N — adequado
para medir como os algoritmos se comportam em diferentes faixas de
dificuldade prática.
"""

import random
from puzzle.state import GOAL_STATE, get_neighbors


def random_walk(n_moves: int, seed: int | None = None, size: int = 4) -> tuple:
    """
    Gera um estado aplicando `n_moves` movimentos aleatórios a partir
    do estado objetivo, sem reverter o último passo.

    Parâmetros
    ----------
    n_moves : int
        Número de movimentos da caminhada.
    seed : int | None
        Semente para reprodutibilidade.
    size : int
        Largura da grade (4 para 15-puzzle).

    Retorno
    -------
    tuple com o estado resultante.
    """
    rng = random.Random(seed)
    state = GOAL_STATE
    previous = None

    for _ in range(n_moves):
        neighbors = get_neighbors(state, size=size)
        # Evita reverter imediatamente o último movimento
        candidates = [nb for nb in neighbors if nb != previous]
        if not candidates:
            candidates = neighbors
        previous = state
        state = rng.choice(candidates)

    return state


def generate_instances(
    difficulties: list[int],
    instances_per_level: int,
    base_seed: int = 0,
    size: int = 4,
) -> list[dict]:
    """
    Gera todas as instâncias do benchmark.

    Retorna lista de dicts com:
      difficulty  : n_moves usado na caminhada
      instance_id : índice da instância (0-based) dentro do nível
      state       : tupla do estado inicial
    """
    instances = []
    for diff in difficulties:
        for i in range(instances_per_level):
            seed = base_seed + diff * 1000 + i
            state = random_walk(diff, seed=seed, size=size)
            instances.append({"difficulty": diff, "instance_id": i, "state": state})
    return instances
