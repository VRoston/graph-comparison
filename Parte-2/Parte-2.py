import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

# =============================================================================
# 1. CARREGAR O GRAFO
# =============================================================================
print("Carregando o arquivo...")

# create_using=nx.Graph() garante que seja não-direcionado (simétrico)
# nodetype=int converte os IDs dos nós para números inteiros
G = nx.read_edgelist('socfb-nips-ego.edges', comments='%', nodetype=int, create_using=nx.Graph())

print(f"Sucesso! Grafo carregado.")
print(f"Número de Nós (N): {G.number_of_nodes()}")
print(f"Número de Arestas (E): {G.number_of_edges()}")

# =============================================================================
# 2. VISUALIZAÇÃO (PLOT)
# =============================================================================
print("Gerando a visualização...")
print("O código para gerar a visualiazação está comentado para evitar lentidão.")

# plt.figure(figsize=(120, 120)) # Tamanho grande para ver detalhes

# # spring_layout tenta separar os nós para mostrar a estrutura
# # k controla a distância entre nós (k maior = mais espaçado)
# pos = nx.spring_layout(G, k=0.15, iterations=20, seed=42)

# nx.draw(G, pos, 
#         node_size=15,           # Nós pequenos para não poluir
#         node_color="blue",      # Cor dos nós
#         edge_color="gray",      # Cor das arestas
#         alpha=0.5,              # Transparência (ajuda a ver densidade)
#         with_labels=False,      # Sem números (ficaria ilegível)
#         width=0.5)              # Arestas finas

# plt.title("Visualização da Rede: socfb-nips-ego")
# plt.savefig("graficos/meu_grafo_real.png") # Salva em arquivo
# print("Gráfico salvo como 'meu_grafo_real.png'")

# =============================================================================
# 3. ANÁLISE RÁPIDA (APLICANDO O QUE APRENDEMOS)
# =============================================================================
print("\n--- Diagnóstico da Rede ---")

# 1. Clustering (Panelinhas)
clustering_avg = nx.average_clustering(G)
print(f"Clustering Médio: {clustering_avg:.4f}")
# Interpretação: Se for alto (>0.3), indica muitos triângulos (comunidades fortes).

# 2. Assortatividade (Quem se conecta com quem)
assortativity = nx.degree_assortativity_coefficient(G)
print(f"Assortatividade: {assortativity:.4f}")
# Interpretação: Se positivo, hubs se conectam a hubs. Se negativo, hubs conectam a nós pequenos.

# 3. Caminho minimo médio
try:
    path_length_avg = nx.average_shortest_path_length(G)
    print(f"Caminho Mínimo Médio: {path_length_avg:.4f}")
except nx.NetworkXError:
    print("Caminho Mínimo Médio: Não é possível calcular (grafo desconectado).")

# 4. É conectado?
if nx.is_connected(G):
    print("Diâmetro: ", nx.diameter(G))
else:
    print("O grafo é desconectado (possui ilhas isoladas).")
    # Pega o maior componente para medir
    largest_cc = max(nx.connected_components(G), key=len)
    subgraph = G.subgraph(largest_cc)
    print(f"Diâmetro do maior componente: {nx.diameter(subgraph)}") 

print("\n--- Análise de Evidências ---")
print(f"1. Clustering médio bem baixo({clustering_avg:.4f})")
print("   → Indica que a rede não tem muitas panelinhas (triângulos).")
print(f"2. Assortatividade negativa({assortativity:.4f})")
print(f"3. Caminho mínimo médio curto ({path_length_avg:.4f})")
print("\n   → Veredito: Ela se comporta como uma Rede Livre de Escala (Scale-Free) com estrutura estelar (hub-and-spoke).")

# Top 3 vértices mais importantes (por grau), na minha opinião!
print("\n--- [Questão A] Quais os 3 vértices mais importantes? ---")
print("Top 3 Vértices Mais Importantes (Por Grau), na minha opinião ¯\_(ツ)_/¯")
# Calcula o grau de todos os nós e ordena do maior para o menor
degree_list = sorted(G.degree, key=lambda x: x[1], reverse=True)

# Pega os 3 primeiros
top_3 = degree_list[:3]

for rank, (node, degree) in enumerate(top_3, 1):
    print(f"Rank {rank}: Nó {node} - Grau: {degree}")

print("\n -> Por que eles são importantes?")
print(f"RESPOSTA: Eles são os 'Hubs' da rede. Como a assortatividade é negativa ({assortativity:.4f}),")
print("a rede depende centralmente desses nós para manter tudo conectado.")
print("Eles funcionam como pontes que unem centenas de nós pequenos.")

print("\n--- [Questão B] Essa rede tende a ser robusta a falhas? ---")
print("RESPOSTA: Depende do tipo de falha.")
print("1. Falhas Aleatórias: SIM. A grande maioria dos nós é pequena e irrelevante.")
print("   Perdê-los não afeta a estrutura.")
print("2. Ataques Direcionados: NÃO. A rede é frágil. Se os Top 3 nós (listados acima)")
print("   forem removidos, a rede provavelmente se fragmentará.")

print("\n--- [Questão C] A difusão de Informação é fácil? ---")
print("RESPOSTA: SIM, muito fácil.")
print(f"Com um caminho médio curto (~{path_length_avg:.4f} passos) e a presença de Hubs centrais,")
print("qualquer informação que chegue a um Hub é rapidamente distribuída para")
print("quase toda a rede instantaneamente.")

print("\n--- [Questão D] A preservação de Informação é fácil? ---")
print("RESPOSTA: NÃO.")
print(f"O baixo clustering ({clustering_avg:.4f}) indica falta de redundância (triângulos).")
print("Se um nó perde sua conexão com o Hub, ele não tem rotas alternativas")
print("locais (amigos de amigos) para recuperar a informação.")

print("\n--- [Questão E] É fácil navegar nessa rede? ---")
print("RESPOSTA: SIM.")
print("A estratégia é simples: 'Vá para o nó mais conectado'. Devido à")
print("estrutura dissortativa, quase todo nó pequeno está a 1 passo de um Hub,")
print("que por sua vez conhece o caminho para o resto da rede.")
print("\n" + "="*60)
