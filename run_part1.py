import networkx as nx
import pandas as pd
import numpy as np
from analysis import get_graph_metrics # Importa sua função

# --- Configuração do Experimento WS ---
N = 1000  # N de nós (mantenha < SLOW_METRICS_THRESHOLD por enquanto)
k = 10    # Grau médio inicial (vizinhos)
p_values = [0, 0.0001, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
seeds = range(10) # 10 seeds para evitar viés amostral

print("Iniciando Experimento Watts-Strogatz...")

# Lista para guardar todos os resultados
all_results = []

for p in p_values:
    print(f"  Processando p = {p}...")
    for seed in seeds:
        # 1. GERAR O GRAFO
        G = nx.watts_strogatz_graph(n=N, k=k, p=p, seed=seed)
        
        # 2. CALCULAR MÉTRICAS
        metrics = get_graph_metrics(G, model_name="Watts-Strogatz")
        
        # 3. ADICIONAR PARÂMETROS DE ENTRADA AO DICIONÁRIO
        metrics['p'] = p
        metrics['k'] = k
        metrics['seed'] = seed
        
        # 4. GUARDAR RESULTADO
        all_results.append(metrics)

print("Experimento concluído. Salvando resultados...")

# 5. SALVAR TUDO EM UM CSV
df = pd.DataFrame(all_results)
df.to_csv('ws_experiment_results.csv', index=False)

print("Resultados salvos em 'ws_experiment_results.csv'")