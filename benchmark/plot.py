"""
Geração de gráficos e tabelas comparativas — BFS × DFS × A*.

Lê os CSVs produzidos por benchmark/run.py e salva figuras em
benchmark/results/figures/ e tabelas LaTeX em benchmark/results/tables/.

Uso
---
    python benchmark/plot.py
"""

import csv
import os
import sys
from collections import defaultdict
from math import sqrt

import matplotlib
matplotlib.use("Agg")          # backend sem janela (compatível com WSL/servidor)
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
FIGURES_DIR = os.path.join(RESULTS_DIR, "figures")
TABLES_DIR  = os.path.join(RESULTS_DIR, "tables")

# ---------------------------------------------------------------------------
# Paleta e estilo
# ---------------------------------------------------------------------------

ALGO_STYLE = {
    "bfs":   {"color": "#2196F3", "marker": "o", "label": "BFS",   "zorder": 3},
    "dfs":   {"color": "#FF5722", "marker": "s", "label": "DFS",   "zorder": 2},
    "astar": {"color": "#4CAF50", "marker": "^", "label": "A*",    "zorder": 4},
}

# Pontos com solve_rate < 1 recebem marcador oco para sinalizar dados parciais
ALPHA_PARTIAL = 0.45

plt.rcParams.update({
    "font.family":      "DejaVu Sans",
    "font.size":        11,
    "axes.titlesize":   13,
    "axes.labelsize":   12,
    "legend.fontsize":  10,
    "figure.dpi":       150,
    "axes.spines.top":  False,
    "axes.spines.right":False,
    "axes.grid":        True,
    "grid.alpha":       0.35,
    "grid.linestyle":   "--",
})

# ---------------------------------------------------------------------------
# Leitura dos dados
# ---------------------------------------------------------------------------

def read_summary(path: str) -> dict[tuple, dict]:
    """Retorna dict keyed por (difficulty, algorithm)."""
    data = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            key = (int(row["difficulty"]), row["algorithm"])
            data[key] = {
                "solve_rate":       float(row["solve_rate"]),
                "avg_nodes":        float(row["avg_nodes"]),
                "avg_solution_len": float(row["avg_solution_len"]) if row["avg_solution_len"] else None,
                "avg_time":         float(row["avg_time"]),
            }
    return data


def read_raw(path: str) -> dict[tuple, list]:
    """Retorna dict keyed por (difficulty, algorithm) com listas de valores brutos."""
    data: dict[tuple, dict] = defaultdict(lambda: {"nodes": [], "times": [], "lengths": []})
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            key = (int(row["difficulty"]), row["algorithm"])
            data[key]["nodes"].append(float(row["nodes_expanded"]))
            data[key]["times"].append(float(row["elapsed_time"]))
            if row["solution_length"]:
                data[key]["lengths"].append(float(row["solution_length"]))
    return data


def stddev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return sqrt(sum((x - mean) ** 2 for x in values) / (len(values) - 1))


# ---------------------------------------------------------------------------
# Helpers de plotagem
# ---------------------------------------------------------------------------

def _series(summary, raw, diffs, algo, metric):
    """
    Retorna (y_values, y_err, partial_mask) para um algoritmo e métrica.
    partial_mask[i] = True se solve_rate < 1.0 naquele ponto.
    """
    y, yerr, partial = [], [], []
    for d in diffs:
        key = (d, algo)
        s   = summary.get(key, {})
        r   = raw.get(key, {})

        if metric == "nodes":
            val = s.get("avg_nodes")
            err = stddev(r.get("nodes", [])) if r else 0.0
        elif metric == "time":
            val = s.get("avg_time")
            err = stddev(r.get("times", [])) if r else 0.0
        elif metric == "length":
            val = s.get("avg_solution_len")
            err = stddev(r.get("lengths", [])) if r else 0.0
        else:
            val = s.get("solve_rate")
            err = 0.0

        y.append(val)
        yerr.append(err)
        partial.append(s.get("solve_rate", 1.0) < 1.0)
    return y, yerr, partial


def _plot_line(ax, diffs, y, yerr, partial, style, log=False):
    """Plota linha com marcadores ocos onde solve_rate < 1."""
    color  = style["color"]
    marker = style["marker"]
    label  = style["label"]

    # Linha e barras de erro (apenas pontos válidos)
    valid_x = [d for d, v in zip(diffs, y) if v is not None]
    valid_y = [v for v in y if v is not None]
    valid_e = [e for v, e in zip(y, yerr) if v is not None]
    valid_p = [p for v, p in zip(y, partial) if v is not None]

    if not valid_x:
        return

    ax.plot(valid_x, valid_y, color=color, linewidth=1.8, zorder=style["zorder"])

    # Marcadores sólidos = totalmente resolvido; ocos = parcial/falhou
    for x, yv, p in zip(valid_x, valid_y, valid_p):
        fc = "white" if p else color
        ax.plot(
            x, yv,
            marker=marker, color=color, markerfacecolor=fc,
            markersize=7, linewidth=1.5, zorder=style["zorder"] + 1,
            label=label if x == valid_x[0] else "_nolegend_",
        )

    # Barras de erro (não em escala log para DFS — desvio cobre vários ordens)
    if not log:
        ax.errorbar(
            valid_x, valid_y, yerr=valid_e,
            fmt="none", color=color, alpha=0.35, capsize=3, zorder=1,
        )


# ---------------------------------------------------------------------------
# Figuras individuais
# ---------------------------------------------------------------------------

def plot_nodes(summary, raw, diffs, out_dir):
    fig, ax = plt.subplots(figsize=(7, 4.5))

    for algo, style in ALGO_STYLE.items():
        y, ye, partial = _series(summary, raw, diffs, algo, "nodes")
        _plot_line(ax, diffs, y, ye, partial, style, log=True)

    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(
        lambda v, _: f"{int(v):,}" if v >= 1 else f"{v:.1f}"
    ))
    ax.set_xlabel("Dificuldade (N movimentos a partir do objetivo)")
    ax.set_ylabel("Nós expandidos (média, escala log)")
    ax.set_title("Nós expandidos por nível de dificuldade")
    ax.set_xticks(diffs)
    _legend(ax)
    _partial_note(ax)
    fig.tight_layout()
    _save(fig, out_dir, "nodes_vs_difficulty.png")


def plot_time(summary, raw, diffs, out_dir):
    fig, ax = plt.subplots(figsize=(7, 4.5))

    for algo, style in ALGO_STYLE.items():
        y, ye, partial = _series(summary, raw, diffs, algo, "time")
        _plot_line(ax, diffs, y, ye, partial, style, log=True)

    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(
        lambda v, _: f"{v:.4f}s" if v < 0.01 else f"{v:.3f}s"
    ))
    ax.set_xlabel("Dificuldade (N movimentos a partir do objetivo)")
    ax.set_ylabel("Tempo de execução (média, escala log)")
    ax.set_title("Tempo de execução por nível de dificuldade")
    ax.set_xticks(diffs)
    _legend(ax)
    _partial_note(ax)
    fig.tight_layout()
    _save(fig, out_dir, "time_vs_difficulty.png")


def plot_solution_length(summary, raw, diffs, out_dir):
    fig, ax = plt.subplots(figsize=(7, 4.5))

    for algo, style in ALGO_STYLE.items():
        y, ye, partial = _series(summary, raw, diffs, algo, "length")
        _plot_line(ax, diffs, y, ye, partial, style, log=False)

    ax.set_xlabel("Dificuldade (N movimentos a partir do objetivo)")
    ax.set_ylabel("Comprimento da solução (média, só resolvidos)")
    ax.set_title("Comprimento da solução por nível de dificuldade")
    ax.set_xticks(diffs)

    # Linha de referência y = x (solução perfeita = N movimentos)
    ax.plot(diffs, diffs, color="gray", linewidth=1, linestyle=":", zorder=0,
            label="y = N (referência)")
    _legend(ax)
    _partial_note(ax)
    fig.tight_layout()
    _save(fig, out_dir, "solution_length_vs_difficulty.png")


def plot_solve_rate(summary, raw, diffs, out_dir):
    fig, ax = plt.subplots(figsize=(7, 4.5))

    for algo, style in ALGO_STYLE.items():
        y, _, _ = _series(summary, raw, diffs, algo, "solve_rate")
        valid_x = [d for d, v in zip(diffs, y) if v is not None]
        valid_y = [v * 100 for v in y if v is not None]
        ax.plot(
            valid_x, valid_y,
            color=style["color"], marker=style["marker"],
            linewidth=1.8, markersize=7, label=style["label"],
            zorder=style["zorder"],
        )

    ax.axhline(100, color="gray", linewidth=0.8, linestyle=":")
    ax.set_ylim(-5, 110)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{int(v)}%"))
    ax.set_xlabel("Dificuldade (N movimentos a partir do objetivo)")
    ax.set_ylabel("Taxa de sucesso (%)")
    ax.set_title("Taxa de sucesso por nível de dificuldade")
    ax.set_xticks(diffs)
    _legend(ax)
    fig.tight_layout()
    _save(fig, out_dir, "solve_rate_vs_difficulty.png")


def plot_combined(summary, raw, diffs, out_dir):
    """Figura combinada 2×2 para o relatório."""
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    fig.suptitle("Comparação BFS × DFS × A* — 15-puzzle", fontsize=14, y=1.01)

    # ── nós expandidos ──────────────────────────────────────────────────────
    ax = axes[0, 0]
    for algo, style in ALGO_STYLE.items():
        y, ye, partial = _series(summary, raw, diffs, algo, "nodes")
        _plot_line(ax, diffs, y, ye, partial, style, log=True)
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(
        lambda v, _: f"{int(v):,}" if v >= 1 else f"{v:.1f}"
    ))
    ax.set_title("Nós expandidos")
    ax.set_xlabel("Dificuldade (N)")
    ax.set_ylabel("Nós (log)")
    ax.set_xticks(diffs)
    _legend(ax)

    # ── tempo ────────────────────────────────────────────────────────────────
    ax = axes[0, 1]
    for algo, style in ALGO_STYLE.items():
        y, ye, partial = _series(summary, raw, diffs, algo, "time")
        _plot_line(ax, diffs, y, ye, partial, style, log=True)
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(
        lambda v, _: f"{v:.4f}s" if v < 0.01 else f"{v:.3f}s"
    ))
    ax.set_title("Tempo de execução")
    ax.set_xlabel("Dificuldade (N)")
    ax.set_ylabel("Tempo (log)")
    ax.set_xticks(diffs)
    _legend(ax)

    # ── comprimento da solução ───────────────────────────────────────────────
    ax = axes[1, 0]
    for algo, style in ALGO_STYLE.items():
        y, ye, partial = _series(summary, raw, diffs, algo, "length")
        _plot_line(ax, diffs, y, ye, partial, style, log=False)
    ax.plot(diffs, diffs, color="gray", linewidth=1, linestyle=":", zorder=0,
            label="y = N")
    ax.set_title("Comprimento da solução")
    ax.set_xlabel("Dificuldade (N)")
    ax.set_ylabel("Movimentos (só resolvidos)")
    ax.set_xticks(diffs)
    _legend(ax)

    # ── taxa de sucesso ───────────────────────────────────────────────────────
    ax = axes[1, 1]
    for algo, style in ALGO_STYLE.items():
        y, _, _ = _series(summary, raw, diffs, algo, "solve_rate")
        valid_x = [d for d, v in zip(diffs, y) if v is not None]
        valid_y = [v * 100 for v in y if v is not None]
        ax.plot(
            valid_x, valid_y,
            color=style["color"], marker=style["marker"],
            linewidth=1.8, markersize=7, label=style["label"],
            zorder=style["zorder"],
        )
    ax.axhline(100, color="gray", linewidth=0.8, linestyle=":")
    ax.set_ylim(-5, 110)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{int(v)}%"))
    ax.set_title("Taxa de sucesso")
    ax.set_xlabel("Dificuldade (N)")
    ax.set_ylabel("Sucesso (%)")
    ax.set_xticks(diffs)
    _legend(ax)

    _partial_note(axes[0, 0], fontsize=8)
    fig.tight_layout()
    _save(fig, out_dir, "all_metrics.png")


# ---------------------------------------------------------------------------
# Tabelas LaTeX
# ---------------------------------------------------------------------------

def make_latex_tables(summary, diffs, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    algos  = ["bfs", "dfs", "astar"]
    labels = {"bfs": "BFS", "dfs": "DFS", "astar": r"A*"}

    # ── Tabela 1: nós expandidos ─────────────────────────────────────────────
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Média de nós expandidos por algoritmo e dificuldade. "
        r"Valores marcados com $\dagger$ indicam que o algoritmo atingiu o "
        r"limite de nós sem encontrar solução.}",
        r"\label{tab:nodes}",
        r"\begin{tabular}{c" + "r" * len(algos) + "}",
        r"\toprule",
        r"$N$ & " + " & ".join(labels[a] for a in algos) + r" \\",
        r"\midrule",
    ]
    for d in diffs:
        cells = []
        for algo in algos:
            s = summary.get((d, algo), {})
            v = s.get("avg_nodes")
            sr = s.get("solve_rate", 1.0)
            if v is None:
                cells.append("—")
            elif sr == 0.0:
                cells.append(f"{v:,.0f}$^\\dagger$")
            else:
                cells.append(f"{v:,.0f}")
        lines.append(f"{d} & " + " & ".join(cells) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    _write_table(lines, out_dir, "tab_nodes.tex")

    # ── Tabela 2: tempo de execução ──────────────────────────────────────────
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Tempo médio de execução (em segundos) por algoritmo e dificuldade.}",
        r"\label{tab:time}",
        r"\begin{tabular}{c" + "r" * len(algos) + "}",
        r"\toprule",
        r"$N$ & " + " & ".join(labels[a] for a in algos) + r" \\",
        r"\midrule",
    ]
    for d in diffs:
        cells = []
        for algo in algos:
            s  = summary.get((d, algo), {})
            v  = s.get("avg_time")
            sr = s.get("solve_rate", 1.0)
            if v is None:
                cells.append("—")
            else:
                fmt = f"{v:.4f}" if v < 0.01 else f"{v:.3f}"
                dag = r"$^\dagger$" if sr == 0.0 else ""
                cells.append(fmt + dag)
        lines.append(f"{d} & " + " & ".join(cells) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    _write_table(lines, out_dir, "tab_time.tex")

    # ── Tabela 3: comprimento da solução + taxa de sucesso ───────────────────
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Comprimento médio da solução (movimentos) e taxa de sucesso "
        r"por algoritmo e dificuldade. Traço indica zero instâncias resolvidas.}",
        r"\label{tab:solution}",
        r"\begin{tabular}{c" + "rl" * len(algos) + "}",
        r"\toprule",
        r"$N$ & "
        + " & ".join(
            rf"\multicolumn{{2}}{{c}}{{{labels[a]}}}" for a in algos
        )
        + r" \\",
        r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(lr){6-7}",
        r" & " + " & ".join([r"mov. & sucesso"] * len(algos)) + r" \\",
        r"\midrule",
    ]
    for d in diffs:
        cells = []
        for algo in algos:
            s  = summary.get((d, algo), {})
            sr = s.get("solve_rate", None)
            sl = s.get("avg_solution_len", None)
            mov = f"{sl:.1f}" if sl is not None else "—"
            pct = f"{sr*100:.0f}\\%" if sr is not None else "—"
            cells.append(f"{mov} & {pct}")
        lines.append(f"{d} & " + " & ".join(cells) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    _write_table(lines, out_dir, "tab_solution.tex")

    print(f"Tabelas LaTeX salvas em: {out_dir}/")


# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------

def _legend(ax, **kwargs):
    handles, labels = ax.get_legend_handles_labels()
    # Remove duplicatas mantendo a ordem
    seen, h2, l2 = set(), [], []
    for h, l in zip(handles, labels):
        if l not in seen and l != "_nolegend_":
            seen.add(l); h2.append(h); l2.append(l)
    ax.legend(h2, l2, **kwargs)


def _partial_note(ax, fontsize=9):
    ax.annotate(
        "◯ marcador oco = solve_rate < 100%",
        xy=(0.01, 0.02), xycoords="axes fraction",
        fontsize=fontsize, color="gray",
    )


def _save(fig, out_dir, filename):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"Figura salva: {path}")


def _write_table(lines: list[str], out_dir: str, filename: str):
    path = os.path.join(out_dir, filename)
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Tabela salva: {path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    summary_path = os.path.join(RESULTS_DIR, "summary.csv")
    results_path = os.path.join(RESULTS_DIR, "results.csv")

    if not os.path.exists(summary_path):
        print(f"Arquivo não encontrado: {summary_path}")
        print("Execute primeiro: python benchmark/run.py")
        sys.exit(1)

    summary = read_summary(summary_path)
    raw     = read_raw(results_path)
    diffs   = sorted({d for d, _ in summary})

    print(f"Níveis de dificuldade: {diffs}")
    print(f"Gerando figuras em:    {FIGURES_DIR}/")
    print()

    plot_nodes(summary, raw, diffs, FIGURES_DIR)
    plot_time(summary, raw, diffs, FIGURES_DIR)
    plot_solution_length(summary, raw, diffs, FIGURES_DIR)
    plot_solve_rate(summary, raw, diffs, FIGURES_DIR)
    plot_combined(summary, raw, diffs, FIGURES_DIR)

    print()
    make_latex_tables(summary, diffs, TABLES_DIR)
    print("\nConcluído.")


if __name__ == "__main__":
    main()
