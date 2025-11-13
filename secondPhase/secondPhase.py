# ...existing code...
import os
import time
import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Usa a função de análise do seu workspace
import analysis
from analysis import get_graph_metrics  # [`get_graph_metrics`](analysis.py)
# Ajusta o limiar para permitir métricas lentas neste script
analysis.SLOW_METRICS_THRESHOLD = 10000  # [`SLOW_METRICS_THRESHOLD`](analysis.py)

# Arquivo de entrada (grafo real)
EDGE_FILE = "socfb-nips-ego.edges"  # [socfb-nips-ego.edges](socfb-nips-ego.edges)

def load_real_graph(path=EDGE_FILE):
    print(f"Carregando grafo de {path} ...")
    G = nx.read_edgelist(path, comments='%', nodetype=int)
    print(f"  N={G.number_of_nodes()}, M={G.number_of_edges()}")
    return G

def basic_stats(G):
    N = G.number_of_nodes()
    M = G.number_of_edges()
    density = nx.density(G)
    degs = np.array([d for _, d in G.degree()])
    return {
        "N": N,
        "M": M,
        "density": density,
        "deg_mean": degs.mean(),
        "deg_median": np.median(degs),
        "deg_max": degs.max()
    }

def degree_power_law_fit(G, kmin=3):
    degs = np.array([d for _, d in G.degree()])
    tail = degs[degs >= kmin]
    if len(tail) < 5:
        return {"alpha": np.nan, "kmin": kmin}
    x = np.log(tail)
    y = np.log(np.arange(1, len(tail)+1))  # rank plot alternative
    # Simples ajuste por regressão em log-log do histograma (apenas estimativa)
    vals, counts = np.unique(tail, return_counts=True)
    mask = vals >= kmin
    if mask.sum() < 3:
        return {"alpha": np.nan, "kmin": kmin}
    log_k = np.log(vals[mask])
    log_pk = np.log(counts[mask] / counts[mask].sum())
    slope, intercept = np.polyfit(log_k, log_pk, 1)
    alpha = -slope  # estimativa grosseira
    return {"alpha": float(alpha), "kmin": int(kmin)}

def compare_with_synthetics(G, seeds=range(10)):
    N = G.number_of_nodes()
    mean_deg = np.mean([d for _, d in G.degree()])
    # parâmetros equivalentes
    p_er = mean_deg / (N - 1)
    k_ws = int(round(mean_deg))
    if k_ws % 2 == 1:
        k_ws += 1
    m_ba = max(1, int(round(mean_deg / 2)))

    print("Parâmetros estimados para sintéticos:",
          f"N={N}, mean_deg={mean_deg:.2f}, ER p={p_er:.6f}, WS k={k_ws}, BA m={m_ba}")

    results = []
    for seed in seeds:
        # ER
        G_er = nx.erdos_renyi_graph(N, p_er, seed=seed)
        m_er = get_graph_metrics(G_er, model_name="ER")
        m_er.update({"model": "ER", "seed": seed, "p": p_er, "k": np.nan, "m": np.nan})
        results.append(m_er)

        # WS
        try:
            G_ws = nx.watts_strogatz_graph(N, k_ws, p=0.1, seed=seed)  # p arbitrary; você pode variar
            m_ws = get_graph_metrics(G_ws, model_name="WS")
            m_ws.update({"model": "WS", "seed": seed, "p": 0.1, "k": k_ws, "m": np.nan})
            results.append(m_ws)
        except Exception:
            pass

        # BA
        try:
            G_ba = nx.barabasi_albert_graph(N, m_ba, seed=seed)
            m_ba = get_graph_metrics(G_ba, model_name="BA")
            m_ba.update({"model": "BA", "seed": seed, "p": np.nan, "k": np.nan, "m": m_ba})
            results.append(m_ba)
        except Exception:
            pass

    df_syn = pd.DataFrame(results)
    return df_syn

def top_k_important_nodes(G, k=3):
    deg = dict(G.degree())
    bt = nx.betweenness_centrality(G, normalized=True)
    try:
        ev = nx.eigenvector_centrality_numpy(G)
    except Exception:
        ev = {n: 0.0 for n in G.nodes()}
    # Normalize and combine
    nodes = list(G.nodes())
    deg_arr = np.array([deg[n] for n in nodes], dtype=float)
    bt_arr = np.array([bt[n] for n in nodes], dtype=float)
    ev_arr = np.array([ev[n] for n in nodes], dtype=float)
    # z-score normalize
    def z(a):
        return (a - a.mean()) / (a.std() + 1e-9)
    score = z(deg_arr) + z(bt_arr) + z(ev_arr)
    idx = np.argsort(score)[::-1][:k]
    top = [(nodes[i], float(score[i]), deg[nodes[i]], bt[nodes[i]], ev[nodes[i]]) for i in idx]
    return top

def robustness_test(G, remove_fraction=0.01):
    # Remove top-degree nodes progressively and track LCC size
    Gc = G.copy()
    N = G.number_of_nodes()
    remove_count = max(1, int(N * remove_fraction))
    lcc_sizes = []
    for i in range(0, remove_count):
        # remove current highest-degree node
        node = max(Gc.degree(), key=lambda x: x[1])[0]
        Gc.remove_node(node)
        comps = list(nx.connected_components(Gc))
        if not comps:
            lcc_sizes.append(0)
        else:
            lcc_sizes.append(len(max(comps, key=len)))
    return lcc_sizes

def main():
    G = load_real_graph()
    stats = basic_stats(G)
    print("Estatísticas básicas:", stats)

    print("Calculando métricas completas do grafo real (pode demorar)...")
    real_metrics = get_graph_metrics(G, model_name="socfb-nips-ego")
    print("Métricas (parciais):", {k: real_metrics.get(k) for k in ['C_avg','C_global','L','D','Assortativity']})

    pl_fit = degree_power_law_fit(G, kmin=3)
    print("Ajuste power-law (estimativa):", pl_fit)

    # Comparação sintética
    df_syn = compare_with_synthetics(G, seeds=range(5))  # muda seeds conforme necessário
    df_syn.to_csv("synthetic_comparison.csv", index=False)
    print("Resultados sintéticos salvos em 'synthetic_comparison.csv'")

    # Top 3 nós importantes
    top3 = top_k_important_nodes(G, k=3)
    print("Top 3 nós importantes (node, combined_score, degree, betweenness, eigenvector):")
    for t in top3:
        print(" ", t)

    # Robustez simples
    lcc_progress = robustness_test(G, remove_fraction=0.02)
    pd.Series(lcc_progress).to_csv("robustness_lcc_progress.csv", index=False)
    print("Teste de robustez salvo em 'robustness_lcc_progress.csv'")

    # Exemplos de plots simples
    plt.figure(figsize=(8,5))
    sns.histplot([d for _, d in G.degree()], bins=50, log_scale=(True, True))
    plt.title("Histograma do grau (log-log)")
    plt.savefig("degree_hist_loglog.png")
    plt.close()

    # Comparação rápida: boxplot de C_avg entre modelos
    if not df_syn.empty:
        plt.figure(figsize=(8,5))
        sns.boxplot(data=df_syn, x='model', y='C_avg')
        plt.title("Comparação: C_avg entre modelos sintéticos")
        plt.savefig("compare_Cavg_models.png")
        plt.close()

    print("Rodou tudo. Veja os arquivos gerados (.csv e .png).")

if __name__ == "__main__":
    main()