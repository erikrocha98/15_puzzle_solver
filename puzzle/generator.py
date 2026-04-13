"""
Geração aleatória de estados iniciais solucionáveis para o 15-puzzle.

Estratégia:
  1. Embaralha aleatoriamente as 16 peças (incluindo o espaço vazio).
  2. Verifica solucionabilidade com a regra de inversões.
  3. Se não for solucionável, corrige trocando as duas primeiras peças
     não-vazias — isso altera a paridade das inversões em 1 sem mover
     o blank, tornando o estado solucionável.

A correção por troca é O(1) e garante que nunca geramos um estado insolúvel,
sem descartar e re-embaralhar.
"""

import random
from .solvability import is_solvable


def generate_random_state(seed: int | None = None) -> tuple:
    """
    Gera e retorna uma configuração inicial aleatória e solucionável.

    Parâmetros
    ----------
    seed : int | None
        Semente para o gerador de números aleatórios (reprodutibilidade).
    """
    if seed is not None:
        random.seed(seed)

    tiles = list(range(16))
    random.shuffle(tiles)
    state = tuple(tiles)

    if not is_solvable(state):
        state = _fix_parity(state)

    return state


def _fix_parity(state: tuple) -> tuple:
    """
    Corrige a paridade de inversões trocando as duas primeiras peças não-vazias.
    Essa troca muda o número de inversões em ±1, invertendo a paridade,
    sem alterar a posição do blank.
    """
    lst = list(state)
    non_blank = [i for i, v in enumerate(lst) if v != 0]
    i, j = non_blank[0], non_blank[1]
    lst[i], lst[j] = lst[j], lst[i]
    return tuple(lst)
