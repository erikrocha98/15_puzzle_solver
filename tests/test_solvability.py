"""
Testes para verificação de solucionabilidade e geração de estados do 15-puzzle.

Estados de referência com solucionabilidade conhecida foram obtidos a partir da
regra matemática e conferidos manualmente.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from puzzle.state import GOAL_STATE
from puzzle.solvability import count_inversions, is_solvable
from puzzle.generator import generate_random_state


# ---------------------------------------------------------------------------
# Testes de count_inversions
# ---------------------------------------------------------------------------

def test_inversions_goal():
    """Estado objetivo tem 0 inversões."""
    assert count_inversions(GOAL_STATE) == 0
    print("count_inversions(GOAL_STATE) = 0 OK")


def test_inversions_known():
    """Estado com inversões conhecidas."""
    # Peças em ordem reversa (sem blank): 15,14,...,1 → C(15,2) = 105 inversões
    state = tuple(range(15, 0, -1)) + (0,)
    assert count_inversions(state) == 105
    print(f"count_inversions(15..1, 0) = {count_inversions(state)} OK")


def test_inversions_ignores_blank():
    """O blank (0) não deve ser contado nas inversões."""
    # Coloca o 0 entre valores altos: não deve alterar a contagem de pares
    state_a = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0)
    state_b = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
    assert count_inversions(state_a) == count_inversions(state_b) == 0
    print("inversões ignoram blank OK")


# ---------------------------------------------------------------------------
# Testes de is_solvable
# ---------------------------------------------------------------------------

def test_goal_is_solvable():
    """Estado objetivo deve ser solucionável."""
    assert is_solvable(GOAL_STATE)
    print("is_solvable(GOAL_STATE) = True OK")


def test_known_solvable():
    """
    Estado 1 passo antes do objetivo (blank e 15 trocados):
    solucionável (1 movimento para resolver).
    """
    # blank na pos 14, 15 na pos 15 → 1 inversão, blank na linha 4 (da base)
    state = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)
    assert is_solvable(state), "Estado a 1 passo do objetivo deve ser solucionável"
    print("is_solvable (1 passo do objetivo) = True OK")


def test_known_unsolvable():
    """
    Trocar as peças 14 e 15 no estado objetivo gera um estado insolúvel.
    Essa é a transformação clássica para criar estados insolúveis.
    """
    # Troca 14 (pos 13) e 15 (pos 14) no estado objetivo
    state = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 14, 0)
    assert not is_solvable(state), "Troca de 14 e 15 deve gerar estado insolúvel"
    print("is_solvable (14 e 15 trocados) = False OK")


def test_known_unsolvable_2():
    """
    Outro estado insolúvel clássico: troca as peças 1 e 2 no estado objetivo.
    """
    state = (2, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0)
    assert not is_solvable(state)
    print("is_solvable (1 e 2 trocados) = False OK")


def test_blank_different_rows():
    """Testa solucionabilidade com blank em linhas diferentes."""
    # blank na linha 1 (topo) — índice 0
    # 0 inversões → blank_row_from_bottom=4 (par) → precisaria de inversões ímpares
    state_unsolvable = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
    assert not is_solvable(state_unsolvable)

    # 1 inversão com blank no topo → solucionável
    state_solvable = (0, 2, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
    assert is_solvable(state_solvable)
    print("blank em linhas diferentes OK")


# ---------------------------------------------------------------------------
# Testes de generate_random_state
# ---------------------------------------------------------------------------

def test_generated_states_are_solvable():
    """100 estados gerados devem ser todos solucionáveis."""
    for i in range(100):
        state = generate_random_state()
        assert is_solvable(state), f"Estado gerado insolúvel: {state}"
    print("100 estados gerados: todos solucionáveis OK")


def test_generated_state_is_valid():
    """Estado gerado deve conter exatamente as peças 0-15."""
    state = generate_random_state()
    assert sorted(state) == list(range(16))
    print("Estado gerado contém peças 0-15 OK")


def test_generated_state_is_tuple():
    """Estado gerado deve ser uma tupla (hashável)."""
    state = generate_random_state()
    assert isinstance(state, tuple)
    hash(state)  # deve ser hashável sem erro
    print("Estado gerado é tuple e hashável OK")


def test_reproducibility():
    """Mesma seed deve gerar o mesmo estado."""
    s1 = generate_random_state(seed=42)
    s2 = generate_random_state(seed=42)
    assert s1 == s2
    print(f"Reproducibilidade com seed=42 OK: {s1}")


def test_variety():
    """Seeds diferentes devem (quase sempre) gerar estados diferentes."""
    states = {generate_random_state(seed=i) for i in range(20)}
    assert len(states) > 1, "Gerador não está produzindo variedade de estados"
    print(f"Variedade: {len(states)} estados distintos em 20 gerações OK")


if __name__ == "__main__":
    print("=" * 50)
    print("Testes de solucionabilidade e geração")
    print("=" * 50)
    test_inversions_goal()
    test_inversions_known()
    test_inversions_ignores_blank()
    print()
    test_goal_is_solvable()
    test_known_solvable()
    test_known_unsolvable()
    test_known_unsolvable_2()
    test_blank_different_rows()
    print()
    test_generated_states_are_solvable()
    test_generated_state_is_valid()
    test_generated_state_is_tuple()
    test_reproducibility()
    test_variety()
    print("=" * 50)
    print("Todos os testes passaram!")
