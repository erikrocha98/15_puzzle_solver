# TP1 — Fundamentos de Inteligência Artificial
**UFMG — Departamento de Engenharia Elétrica**
Prof. Cristiano Castro — 2026/1

Implementação de agentes para resolver o **15-puzzle** (quebra-cabeça de 15 peças) utilizando diferentes algoritmos de busca.

---

## Estrutura do projeto

```
tp-fund-ia/
├── puzzle/
│   ├── __init__.py
│   ├── state.py          # Modelagem do estado
│   ├── solvability.py    # Verificação de solucionabilidade (Tarefa 1)
│   ├── generator.py      # Geração aleatória de estados (Tarefa 2)
│   └── search/
│       ├── __init__.py
│       ├── bfs.py        # Busca em largura — BFS (Tarefa 3)
│       ├── dfs.py        # Busca em profundidade — DFS (Tarefa 3)
│       └── astar.py      # Busca A* com heurística Manhattan (Tarefa 4)
├── tests/
│   ├── test_state.py         # Testes da modelagem
│   ├── test_solvability.py   # Testes de solucionabilidade e geração
│   ├── test_bfs.py           # Testes de BFS (8-puzzle e 15-puzzle)
│   ├── test_dfs.py           # Testes de DFS (8-puzzle e 15-puzzle)
│   └── test_astar.py         # Testes de A* e heurística Manhattan
└── README.md
```

---

## Dia 1 — Modelagem e estrutura do projeto

### Representação do estado

O estado do jogo é representado como uma **tupla de 16 inteiros** (`tuple[int]`), onde cada posição corresponde a uma célula da grade 4×4 lida da esquerda para a direita e de cima para baixo. O valor `0` representa o espaço vazio.

```
índices:        exemplo de estado:
 0  1  2  3      1  2  3  4
 4  5  6  7      5  6  7  8
 8  9 10 11      9 10 11 12
12 13 14 15     13 14 15  _
```

A escolha por `tuple` (em vez de lista ou matriz) é deliberada: tuplas são **hasháveis**, o que permite armazená-las diretamente em `set` e `dict` — estruturas essenciais para detectar estados visitados e evitar ciclos nos algoritmos de busca.

### Estado objetivo

```python
GOAL_STATE = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0)
```

As peças estão ordenadas de 1 a 15, com o espaço vazio na última posição.

### Funções implementadas (`puzzle/state.py`)

| Função | Descrição |
|--------|-----------|
| `find_blank(state)` | Retorna o índice do espaço vazio (`0`) no estado |
| `get_neighbors(state)` | Retorna lista de estados obtidos por movimentos válidos |
| `is_goal(state)` | Verifica se o estado é o estado objetivo |
| `print_state(state)` | Imprime o estado em formato de grade 4×4 |

### Geração de vizinhos

A função `get_neighbors` identifica a posição do espaço vazio (linha e coluna via `divmod`), e gera até 4 vizinhos deslocando o blank nas direções válidas:

- **Cima**: possível se `linha > 0` → troca com índice `blank - 4`
- **Baixo**: possível se `linha < 3` → troca com índice `blank + 4`
- **Esquerda**: possível se `coluna > 0` → troca com índice `blank - 1`
- **Direita**: possível se `coluna < 3` → troca com índice `blank + 1`

Posições de canto geram **2 vizinhos**, bordas geram **3**, e posições internas geram **4**.

### Testes realizados

Os testes em `tests/test_state.py` verificaram:
- Formato e valor do estado objetivo
- Localização correta do espaço vazio em diferentes posições
- Número correto de vizinhos para cantos (2), bordas (3) e centro (4)
- Identidade dos estados vizinhos gerados (valores conferidos manualmente)

Todos os testes passaram com sucesso.

---

## Dia 2 — Tarefa 1 (solucionabilidade) + Tarefa 2 (geração aleatória)

### Tarefa 1 — Verificação de solucionabilidade (`puzzle/solvability.py`)

Para um grid de largura par (N = 4), a solucionabilidade depende de dois fatores combinados:

1. **Número de inversões**: um par (i, j) com i < j é uma inversão quando `state[i] > state[j]`, desconsiderando o espaço vazio. A contagem é feita em O(n²) sobre a sequência de peças sem o blank.

2. **Linha do espaço vazio a partir de baixo** (base 1): calculada como `SIZE - (blank_index // SIZE)`.

**Condição de solucionabilidade:**

```
(inversions + blank_row_from_bottom) % 2 == 1
```

Isso equivale a:
- blank em linha **ímpar** do fundo → inversões devem ser **pares**
- blank em linha **par** do fundo   → inversões devem ser **ímpares**

Verificação com o estado objetivo: 0 inversões + linha 1 (ímpar) → (0+1) % 2 = 1 ✓

| Função | Descrição |
|--------|-----------|
| `count_inversions(state)` | Conta pares fora de ordem, ignorando o blank |
| `is_solvable(state)` | Aplica a regra e retorna `True`/`False` |

### Tarefa 2 — Geração aleatória de estados (`puzzle/generator.py`)

A estratégia adotada foi:

1. Embaralha aleatoriamente as 16 peças com `random.shuffle`.
2. Verifica solucionabilidade com `is_solvable`.
3. Se insolúvel, **corrige a paridade** trocando as duas primeiras peças não-vazias — isso muda o número de inversões em 1 (inverte a paridade) sem alterar a posição do blank, tornando o estado solucionável.

Essa abordagem é O(1) para a correção e evita o descarte e re-embaralhamento de estados.

A função aceita um parâmetro opcional `seed` para reprodutibilidade dos experimentos.

```python
state = generate_random_state()          # estado aleatório solucionável
state = generate_random_state(seed=42)   # reprodutível
```

### Testes realizados

Os testes em `tests/test_solvability.py` cobriram:
- Estado objetivo com 0 inversões
- Estado com inversões contadas manualmente (15..1 → 105 inversões)
- Verificação de que o blank é ignorado na contagem
- Estados solucionáveis e insolúveis conhecidos (troca de peças adjacentes no objetivo)
- Blank em linhas diferentes com paridades variadas
- 100 estados gerados aleatoriamente: todos solucionáveis
- Validade (exatamente as peças 0–15), tipo `tuple`, hashabilidade
- Reprodutibilidade (mesma seed → mesmo estado) e variedade (seeds diferentes → estados diferentes)

Todos os testes passaram com sucesso.

---

## Dia 3 — Tarefa 3: Busca em Largura (BFS)

### Algoritmo (`puzzle/search/bfs.py`)

BFS explora o grafo de estados camada por camada, garantindo que a primeira
solução encontrada seja a de menor número de movimentos (ótima).

Estruturas utilizadas:
- `collections.deque` como fila FIFO para os estados a expandir.
- `dict` `parent[state] = predecessor` para registrar o caminho e evitar
  revisitar estados (funciona como conjunto de visitados e como estrutura de
  reconstrução ao mesmo tempo).

O caminho é reconstruído percorrendo o dicionário `parent` do estado objetivo
até o estado inicial e invertendo a lista resultante.

A busca retorna um dicionário com quatro métricas:

| Campo | Descrição |
|-------|-----------|
| `solution` | Lista de estados do inicial ao objetivo, ou `None` |
| `nodes_expanded` | Número de nós expandidos |
| `solution_length` | Número de movimentos até a solução, ou `None` |
| `elapsed_time` | Tempo de execução em segundos |

Um parâmetro `max_nodes` (padrão: 500 000) interrompe a busca caso o limite
seja atingido, evitando travamento em casos intratáveis.

O parâmetro `size` (padrão: 4) permite usar o mesmo código para o 8-puzzle
(size=3), facilitando validação com soluções conhecidas.

```python
from puzzle.search import bfs
from puzzle.state import GOAL_STATE

result = bfs(initial_state)
# result['solution']        → lista de estados
# result['nodes_expanded']  → int
# result['solution_length'] → int
# result['elapsed_time']    → float
```

### Limitações do BFS no 15-puzzle

BFS é **completo** e **ótimo**, mas sua complexidade de tempo e espaço é
exponencial em função da profundidade da solução. Para o 15-puzzle, soluções
com mais de ~20 movimentos tornam o consumo de memória impraticável. Por isso,
os testes cobrem apenas configurações fáceis (poucos movimentos do objetivo).

### Testes realizados (`tests/test_bfs.py`)

- **8-puzzle (3×3)**: estados a 0, 1, 2 e 4 movimentos do objetivo com soluções
  conferidas manualmente; caminho conectado; comportamento correto sob limite
  de nós; coerência das métricas.
- **15-puzzle (4×4)**: estados a 1, 2 e 5 movimentos do objetivo; caminho
  conectado; crescimento dos nós expandidos com a profundidade.

Todos os testes passaram com sucesso.

---

## Dia 4 — Tarefa 3: Busca em Profundidade (DFS)


### Algoritmo (`puzzle/search/dfs.py`)

DFS explora o grafo de estados descendo o mais fundo possível em cada ramo
antes de retroceder. Utiliza uma **pilha explícita** (lista Python com `append`/`pop`).

Estruturas utilizadas:
- `list` como pilha LIFO. Cada entrada armazena `(state, path)`, onde `path`
  é a tupla de estados desde o inicial até o atual.
- `set(path)` — derivado do caminho a cada expansão — para detectar ciclos
  **no caminho atual** em O(1). Estados visitados em outros ramos podem ser
  revisitados, preservando o comportamento natural do DFS.

Dois limites controlam a busca:

| Parâmetro | Padrão | Descrição |
|-----------|--------|-----------|
| `max_depth` | 50 | Profundidade máxima. Nós além desse nível não são expandidos. |
| `max_nodes` | 500 000 | Nós expandidos totais. Interrompe a busca se excedido. |

O retorno segue o mesmo contrato do BFS (`solution`, `nodes_expanded`,
`solution_length`, `elapsed_time`), facilitando a comparação entre os algoritmos.

### Diferenças em relação ao BFS

| Propriedade | BFS | DFS |
|-------------|-----|-----|
| Ótimo | Sim (menor nº de movimentos) | Não |
| Completo | Sim (dentro do limite de nós) | Sim (com limite de profundidade) |
| Memória | O(b^d) — alto | O(b·m) — baixo |
| 15-puzzle prático | Casos fáceis | Apenas 1–2 movimentos do objetivo |

### Limitação observada no 15-puzzle

DFS é impraticável para o 15-puzzle mesmo para estados a poucos movimentos
do objetivo. Por explorar primeiro ramos de profundidade 50, o algoritmo
esgota `max_nodes` antes de encontrar a solução ótima. Esse comportamento
foi documentado em `test_15_impractical_for_deeper_states`.

### Testes realizados (`tests/test_dfs.py`)

- **8-puzzle (3×3)**: estados a 0, 1, 2 e 4 movimentos do objetivo; caminho
  conectado; solução ≥ BFS (não-otimalidade confirmada); limite de
  profundidade e de nós funcionando corretamente.
- **15-puzzle (4×4)**: estados a 1 e 2 movimentos do objetivo; caminho
  conectado; teste documentando a impraticabilidade para estados mais distantes.

Todos os testes passaram com sucesso.

---

## Dia 5 — Tarefa 4: Busca A* (`puzzle/search/astar.py`)

### Função de custo e heurística

| Função | Definição |
|--------|-----------|
| `g(n)` | Profundidade do nó — número de movimentos desde o estado inicial |
| `h(n)` | Distância de Manhattan — para cada peça (exceto o blank), soma `\|linha_atual − linha_obj\|` + `\|col_atual − col_obj\|` |
| `f(n)` | `g(n) + h(n)` — prioridade na fila |

A heurística de Manhattan é **admissível** (nunca superestima o custo real) e **consistente**, garantindo que A* encontre sempre a solução ótima.

### Algoritmo (`puzzle/search/astar.py`)

Estruturas utilizadas:
- `heapq` como fila de prioridade mínima. Cada entrada é `(f, g, counter, state)`.
  O campo `counter` desempata quando `f` e `g` são iguais, evitando a comparação direta de tuplas de estado.
- `g_score[state]` — menor custo conhecido até cada estado, usado para descartar entradas desatualizadas do heap (*lazy deletion*).
- `parent[state]` — estado predecessor no caminho ótimo, para reconstrução da solução.

O retorno segue o mesmo contrato de BFS e DFS:

| Campo | Descrição |
|-------|-----------|
| `solution` | Lista de estados do inicial ao objetivo, ou `None` |
| `nodes_expanded` | Número de nós expandidos |
| `solution_length` | Número de movimentos até a solução, ou `None` |
| `elapsed_time` | Tempo de execução em segundos |

```python
from puzzle.search.astar import astar, manhattan_distance
from puzzle.state import GOAL_STATE

result = astar(initial_state)
# result['solution']        → lista de estados
# result['nodes_expanded']  → int
# result['solution_length'] → int
# result['elapsed_time']    → float
```

### Vantagem sobre BFS e DFS

A heurística guia a busca diretamente para a solução, expandindo uma fração ínfima dos nós que BFS precisaria. Exemplo com instância a 20 movimentos do objetivo:

| Algoritmo | Nós expandidos | Resultado |
|-----------|---------------|-----------|
| BFS | 500 000 | falhou |
| DFS | 500 000 | falhou |
| **A\*** | **574** | **20 movimentos (ótimo)** |

### Testes realizados (`tests/test_astar.py`)

- **Heurística**: valor zero no estado objetivo; valor correto a 1 movimento; admissibilidade verificada contra BFS em 20 instâncias aleatórias.
- **8-puzzle (3×3)**: estados a 0, 1, 2 e 4 movimentos; caminho conectado; limite de nós; otimalidade idêntica ao BFS; A* expande menos nós que BFS.
- **15-puzzle (4×4)**: estados a 1 e 5 movimentos; caminho conectado; otimalidade idêntica ao BFS.
- **Instância difícil**: A* resolve em 574 nós uma instância que BFS não consegue em 500 000.

Todos os testes passaram com sucesso.
