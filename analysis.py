import networkx as nx
import numpy as np

# Limite de nós para rodar métricas lentas
# Ajuste conforme seu PC. Comece baixo (ex: 1500).
SLOW_METRICS_THRESHOLD = 1500

def get_graph_metrics(G, model_name="unknown"):
    """
    Recebe um grafo G do NetworkX e retorna um dicionário com 
    todas as métricas de interesse.
    """
    metrics = {
        'model': model_name,
        'N': G.number_of_nodes(),
        'M': G.number_of_edges(),
        'C_global': np.nan,  # Coeficiente de Clusterização Global (Transitivity)
        'C_avg': np.nan,     # Média dos Coeficientes de Clusterização Locais
        'L': np.nan,         # Caminho Médio Mais Curto
        'D': np.nan,         # Diâmetro
        'Assortativity': np.nan,
        'is_connected': False
    }

    # Métricas rápidas (sempre rodam)
    try:
        metrics['C_global'] = nx.transitivity(G)
    except Exception:
        pass # Pode falhar em grafos muito pequenos ou vazios

    try:
        metrics['C_avg'] = nx.average_clustering(G)
    except Exception:
        pass
        
    try:
        metrics['Assortativity'] = nx.degree_assortativity_coefficient(G)
    except Exception:
        pass # Pode falhar se o grau for constante (ex: anel)

    # --- Métricas Lentas ---
    # Só rodam se o grafo for pequeno o suficiente
    if G.number_of_nodes() < SLOW_METRICS_THRESHOLD:
        
        is_connected = nx.is_connected(G)
        metrics['is_connected'] = is_connected

        if is_connected:
            # Se for conectado, podemos calcular L e D diretamente
            try:
                metrics['L'] = nx.average_shortest_path_length(G)
                metrics['D'] = nx.diameter(G)
            except Exception:
                pass # Segurança
        else:
            # Se for desconectado, pegamos o Componente Gigante (LCC)
            try:
                # Pega o maior subgrafo conectado (LCC)
                components = nx.connected_components(G)
                largest_cc_nodes = max(components, key=len)
                LCC = G.subgraph(largest_cc_nodes)
                
                # Calcula as métricas *apenas no LCC*
                metrics['L'] = nx.average_shortest_path_length(LCC)
                metrics['D'] = nx.diameter(LCC)
            except Exception:
                pass # Pode falhar se o LCC for trivial
    
    return metrics