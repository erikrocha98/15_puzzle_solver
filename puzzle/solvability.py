"""
Verificação de solucionabilidade do 15-puzzle.

Regra (grade de largura par, N=4):
  Seja:
    - inversions: número de pares (i, j) com i < j onde state[i] > state[j],
                  ignorando o espaço vazio (0).
    - blank_row_from_bottom: linha do espaço vazio contada de baixo para cima,
                             com base 1 (última linha = 1, antepenúltima = 2, ...).

  O estado é solucionável se e somente se:
    (inversions + blank_row_from_bottom) é ímpar

  Equivalentemente:
    - blank em linha ímpar do fundo  → inversions deve ser par
    - blank em linha par do fundo    → inversions deve ser ímpar
"""

from .state import SIZE


def count_inversions(state: tuple) -> int:
    """
    Conta o número de inversões na sequência de peças, ignorando o espaço vazio.

    Uma inversão é um par (i, j) com i < j tal que state[i] > state[j],
    desconsiderando posições onde o valor é 0.
    """
    tiles = [v for v in state if v != 0]
    inversions = 0
    for i in range(len(tiles)):
        for j in range(i + 1, len(tiles)):
            if tiles[i] > tiles[j]:
                inversions += 1
    return inversions


def is_solvable(state: tuple) -> bool:
    """
    Retorna True se o estado é solucionável, False caso contrário.

    Para o 15-puzzle (grade 4x4, largura par), a condição é:
        (número de inversões + linha do blank a partir de baixo) deve ser ímpar.
    """
    blank_index = state.index(0)
    blank_row_from_top = blank_index // SIZE          # 0-indexed de cima
    blank_row_from_bottom = SIZE - blank_row_from_top  # 1-indexed de baixo

    inversions = count_inversions(state)
    return (inversions + blank_row_from_bottom) % 2 == 1
