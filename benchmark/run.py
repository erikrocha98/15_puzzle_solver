"""
Benchmark comparativo: BFS × DFS × A* no 15-puzzle.

Uso
---
    python benchmark/run.py                  # executa com configurações padrão
    python benchmark/run.py --instances 5    # 5 instâncias por nível

Saída
-----
  benchmark/results/results.csv   — uma linha por (instância, algoritmo)
  benchmark/results/summary.csv   — médias agrupadas por (dificuldade, algoritmo)

Imprime também uma tabela de resumo no terminal.
"""

import argparse
import csv
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from benchmark.generator import generate_instances
from puzzle.search.bfs import bfs
from puzzle.search.dfs import dfs
from puzzle.search.astar import astar

# ---------------------------------------------------------------------------
# Configurações padrão
# ---------------------------------------------------------------------------

DIFFICULTIES      = [5, 10, 15, 20, 25, 30, 40, 50]
INSTANCES_PER_LVL = 10
MAX_NODES         = 500_000
DFS_MAX_NODES     = 100_000     # DFS falha cedo; limite menor economiza tempo
DFS_MAX_DEPTH     = 80          # profundidade máxima generosa para DFS

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")

# ---------------------------------------------------------------------------
# Execução de um único algoritmo em um único estado
# ---------------------------------------------------------------------------

def run_one(algorithm: str, state: tuple) -> dict:
    """Roda o algoritmo e devolve as métricas normalizadas."""
    if algorithm == "bfs":
        result = bfs(state, max_nodes=MAX_NODES)
    elif algorithm == "dfs":
        result = dfs(state, max_nodes=DFS_MAX_NODES, max_depth=DFS_MAX_DEPTH)
    elif algorithm == "astar":
        result = astar(state, max_nodes=MAX_NODES)
    else:
        raise ValueError(f"Algoritmo desconhecido: {algorithm}")

    return {
        "algorithm":      algorithm,
        "solved":         result["solution"] is not None,
        "nodes_expanded": result["nodes_expanded"],
        "solution_length": result["solution_length"],   # None se falhou
        "elapsed_time":   result["elapsed_time"],
    }


# ---------------------------------------------------------------------------
# Runner principal
# ---------------------------------------------------------------------------

def run_benchmark(difficulties, instances_per_level, verbose=True):
    instances = generate_instances(difficulties, instances_per_level)
    total = len(instances) * 3  # três algoritmos
    done  = 0

    rows = []   # dados brutos, um por (instância × algoritmo)

    for inst in instances:
        diff  = inst["difficulty"]
        idx   = inst["instance_id"]
        state = inst["state"]

        for algo in ("bfs", "dfs", "astar"):
            metrics = run_one(algo, state)
            row = {
                "difficulty":      diff,
                "instance_id":     idx,
                "algorithm":       algo,
                "solved":          metrics["solved"],
                "nodes_expanded":  metrics["nodes_expanded"],
                "solution_length": metrics["solution_length"] if metrics["solved"] else "",
                "elapsed_time":    f"{metrics['elapsed_time']:.6f}",
            }
            rows.append(row)
            done += 1
            if verbose:
                status = (
                    f"len={metrics['solution_length']:3d}"
                    if metrics["solved"]
                    else "FAILED"
                )
                print(
                    f"  [{done:4d}/{total}] diff={diff:2d} inst={idx} "
                    f"{algo:<6s}  nodes={metrics['nodes_expanded']:>8,d}  "
                    f"{status}  t={metrics['elapsed_time']:.4f}s"
                )

    return rows


# ---------------------------------------------------------------------------
# Persistência dos resultados
# ---------------------------------------------------------------------------

def save_results(rows: list[dict], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fieldnames = [
        "difficulty", "instance_id", "algorithm",
        "solved", "nodes_expanded", "solution_length", "elapsed_time",
    ]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nResultados brutos salvos em: {path}")


def build_summary(rows: list[dict]) -> list[dict]:
    """
    Agrega métricas por (difficulty, algorithm):
      - solve_rate       : fração de instâncias resolvidas
      - avg_nodes        : média de nós expandidos (todas as instâncias)
      - avg_solution_len : média do comprimento da solução (só resolvidas)
      - avg_time         : média do tempo de execução (todas as instâncias)
    """
    from collections import defaultdict

    buckets: dict[tuple, dict] = defaultdict(lambda: {
        "nodes": [], "lengths": [], "times": [], "solved": 0, "total": 0
    })

    for r in rows:
        key = (r["difficulty"], r["algorithm"])
        b   = buckets[key]
        b["total"]  += 1
        b["nodes"].append(int(r["nodes_expanded"]))
        b["times"].append(float(r["elapsed_time"]))
        if r["solved"] in (True, "True"):
            b["solved"] += 1
            if r["solution_length"] not in ("", None):
                b["lengths"].append(int(r["solution_length"]))

    summary = []
    for (diff, algo), b in sorted(buckets.items()):
        summary.append({
            "difficulty":       diff,
            "algorithm":        algo,
            "solve_rate":       f"{b['solved'] / b['total']:.2f}",
            "avg_nodes":        f"{sum(b['nodes']) / len(b['nodes']):.1f}",
            "avg_solution_len": f"{sum(b['lengths']) / len(b['lengths']):.1f}" if b["lengths"] else "",
            "avg_time":         f"{sum(b['times'])  / len(b['times']):.4f}",
        })
    return summary


def save_summary(summary: list[dict], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fieldnames = [
        "difficulty", "algorithm",
        "solve_rate", "avg_nodes", "avg_solution_len", "avg_time",
    ]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary)
    print(f"Resumo salvo em: {path}")


# ---------------------------------------------------------------------------
# Impressão da tabela de resumo no terminal
# ---------------------------------------------------------------------------

def print_summary_table(summary: list[dict]) -> None:
    algos = ("bfs", "dfs", "astar")
    diffs = sorted({int(r["difficulty"]) for r in summary})

    header_cols = ["diff"] + [f"{a:<22s}" for a in algos]
    sub_header  = "     " + "".join(
        f"  {'solve':>5} {'nodes':>10} {'len':>6} {'t(s)':>8}  "
        for _ in algos
    )

    sep = "-" * (5 + 40 * len(algos))
    print()
    print("=" * len(sep))
    print("  RESUMO DO BENCHMARK — 15-puzzle")
    print("=" * len(sep))
    print(sub_header)
    print(sep)

    # indexar por (diff, algo)
    idx = {(int(r["difficulty"]), r["algorithm"]): r for r in summary}

    for diff in diffs:
        line = f"{diff:>4d} "
        for algo in algos:
            r = idx.get((diff, algo), {})
            solve = r.get("solve_rate", "-")
            nodes = r.get("avg_nodes", "-")
            slen  = r.get("avg_solution_len", "-") or "-"
            t     = r.get("avg_time", "-")
            line += f"  {solve:>5} {nodes:>10} {slen:>6} {t:>8}  "
        print(line)

    print(sep)
    print("  solve=taxa de sucesso  nodes=nós expandidos (média)")
    print("  len=movimentos (média, só resolvidos)  t=tempo em segundos")
    print()


# ---------------------------------------------------------------------------
# Identificação do ponto de falha
# ---------------------------------------------------------------------------

def print_failure_analysis(summary: list[dict]) -> None:
    print("ANÁLISE: primeiro nível onde cada algoritmo falha (solve_rate < 1.0)")
    print("-" * 55)
    for algo in ("bfs", "dfs", "astar"):
        rows_algo = sorted(
            [r for r in summary if r["algorithm"] == algo],
            key=lambda r: int(r["difficulty"])
        )
        failing = [r for r in rows_algo if float(r["solve_rate"]) < 1.0]
        if failing:
            first = failing[0]
            print(
                f"  {algo:<6s}: falha a partir de dificuldade "
                f"{first['difficulty']:>2d}  "
                f"(solve_rate={first['solve_rate']})"
            )
        else:
            print(f"  {algo:<6s}: resolveu todos os níveis testados")
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Benchmark BFS × DFS × A*")
    parser.add_argument(
        "--instances", type=int, default=INSTANCES_PER_LVL,
        help=f"Instâncias por nível de dificuldade (padrão: {INSTANCES_PER_LVL})",
    )
    parser.add_argument(
        "--difficulties", type=int, nargs="+", default=DIFFICULTIES,
        help="Níveis de dificuldade (n_moves)",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Não imprime linha por linha durante a execução",
    )
    args = parser.parse_args()

    print(f"Dificuldades : {args.difficulties}")
    print(f"Instâncias/nível : {args.instances}")
    print(f"max_nodes={MAX_NODES:,}  DFS max_nodes={DFS_MAX_NODES:,}  DFS max_depth={DFS_MAX_DEPTH}")
    print()

    t0   = time.perf_counter()
    rows = run_benchmark(args.difficulties, args.instances, verbose=not args.quiet)
    elapsed = time.perf_counter() - t0

    print(f"\nTempo total: {elapsed:.1f}s")

    results_path = os.path.join(RESULTS_DIR, "results.csv")
    summary_path = os.path.join(RESULTS_DIR, "summary.csv")

    save_results(rows, results_path)
    summary = build_summary(rows)
    save_summary(summary, summary_path)

    print_summary_table(summary)
    print_failure_analysis(summary)


if __name__ == "__main__":
    main()
