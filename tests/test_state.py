"""Testes manuais para a modelagem do estado do 15-puzzle."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from puzzle.state import GOAL_STATE, find_blank, get_neighbors, is_goal, print_state


def test_goal_state():
    assert GOAL_STATE == (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0)
    print("Estado objetivo:")
    print_state(GOAL_STATE)


def test_find_blank():
    # blank no final (estado objetivo)
    assert find_blank(GOAL_STATE) == 15

    # blank no início
    state = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
    assert find_blank(state) == 0

    # blank no meio
    state = (1, 2, 3, 4, 5, 0, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
    assert find_blank(state) == 5
    print("find_blank OK")


def test_is_goal():
    assert is_goal(GOAL_STATE)
    assert not is_goal((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15))
    print("is_goal OK")


def test_neighbors_corner():
    """Blank no canto superior esquerdo (índice 0): apenas 2 vizinhos."""
    state = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
    neighbors = get_neighbors(state)
    assert len(neighbors) == 2, f"Esperado 2 vizinhos, obtido {len(neighbors)}"

    # blank desce → troca com índice 4
    expected_down = (4, 1, 2, 3, 0, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
    # blank vai para direita → troca com índice 1
    expected_right = (1, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
    assert expected_down in neighbors
    assert expected_right in neighbors
    print("Vizinhos (canto sup-esq) OK — 2 vizinhos")


def test_neighbors_center():
    """Blank no centro (índice 5): deve ter 4 vizinhos."""
    state = (1, 2, 3, 4, 5, 0, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
    neighbors = get_neighbors(state)
    assert len(neighbors) == 4, f"Esperado 4 vizinhos, obtido {len(neighbors)}"
    print("Vizinhos (centro) OK — 4 vizinhos")


def test_neighbors_goal():
    """Blank no canto inferior direito (estado objetivo): apenas 2 vizinhos."""
    neighbors = get_neighbors(GOAL_STATE)
    assert len(neighbors) == 2, f"Esperado 2 vizinhos, obtido {len(neighbors)}"

    # blank sobe → troca com índice 11
    expected_up = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 13, 14, 15, 12)
    # blank vai para esquerda → troca com índice 14
    expected_left = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)
    assert expected_up in neighbors
    assert expected_left in neighbors
    print("Vizinhos (estado objetivo) OK — 2 vizinhos")
    print("\nVizinhos do estado objetivo:")
    for n in neighbors:
        print_state(n)


def test_neighbors_edge():
    """Blank na borda direita (índice 7): deve ter 3 vizinhos."""
    state = (1, 2, 3, 4, 5, 6, 7, 0, 8, 9, 10, 11, 12, 13, 14, 15)
    neighbors = get_neighbors(state)
    assert len(neighbors) == 3, f"Esperado 3 vizinhos, obtido {len(neighbors)}"
    print("Vizinhos (borda direita) OK — 3 vizinhos")


if __name__ == "__main__":
    print("=" * 40)
    print("Testes de modelagem do 15-puzzle")
    print("=" * 40)
    test_goal_state()
    test_find_blank()
    test_is_goal()
    test_neighbors_corner()
    test_neighbors_center()
    test_neighbors_goal()
    test_neighbors_edge()
    print("=" * 40)
    print("Todos os testes passaram!")
