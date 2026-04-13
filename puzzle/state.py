"""
Representação de estado para o 15-puzzle.

O estado é uma tupla de 16 inteiros (0..15), onde 0 representa o espaço vazio.
A leitura é em ordem de linha, da esquerda para a direita, de cima para baixo:

  índices:
   0  1  2  3
   4  5  6  7
   8  9 10 11
  12 13 14 15

Estado objetivo:
   1  2  3  4
   5  6  7  8
   9 10 11 12
  13 14 15  _
"""

# Estado objetivo: peças 1-15 em ordem, espaço vazio na última posição
GOAL_STATE = tuple(range(1, 16)) + (0,)

# Tamanho da grade
SIZE = 4


def find_blank(state: tuple) -> int:
    """Retorna o índice do espaço vazio (0) no estado."""
    return state.index(0)


def get_neighbors(state: tuple, size: int = SIZE) -> list[tuple]:
    """
    Gera todos os estados vizinhos válidos a partir de um estado.
    Um vizinho é obtido deslocando o espaço vazio em uma das quatro
    direções possíveis (cima, baixo, esquerda, direita).

    O parâmetro `size` permite usar a função com grids de tamanho
    diferente de 4×4 (e.g., size=3 para o 8-puzzle).
    """
    blank = find_blank(state)
    row, col = divmod(blank, size)
    neighbors = []

    moves = []
    if row > 0:             # move blank para cima (peça de cima desce)
        moves.append(blank - size)
    if row < size - 1:      # move blank para baixo (peça de baixo sobe)
        moves.append(blank + size)
    if col > 0:             # move blank para esquerda (peça da esq. vai para direita)
        moves.append(blank - 1)
    if col < size - 1:      # move blank para direita (peça da dir. vai para esquerda)
        moves.append(blank + 1)

    for target in moves:
        lst = list(state)
        lst[blank], lst[target] = lst[target], lst[blank]
        neighbors.append(tuple(lst))

    return neighbors


def is_goal(state: tuple) -> bool:
    """Verifica se o estado é o estado objetivo."""
    return state == GOAL_STATE


def print_state(state: tuple) -> None:
    """Imprime o estado em formato de grade 4x4."""
    for i in range(SIZE):
        row = state[i * SIZE:(i + 1) * SIZE]
        print(" ".join(f"{v:2d}" if v != 0 else "  " for v in row))
    print()
