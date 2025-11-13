# Parte 2 — Comparação do grafo socfb-nips-ego

Fonte: https://networkrepository.com/socfb-nips-ego.php

## Estatísticas principais (resultado do script)
- N = 2888, M = 2981, mean_deg ≈ 2.06, deg_median = 1, deg_max = 769  
- Clustering médio C_avg ≈ 0.027, clustering global C_global ≈ 3.6e-4  
- Comprimento médio de caminho L ≈ 3.87, diâmetro D = 9  
- Assortatividade ≈ -0.668 (fortemente desassortativo)

## Evidências / classificação (scale‑free / small‑world / aleatório)
- Scale‑free (livre de escala): evidência mista. Há cauda pesada (máx de grau muito alto, hubs claros) indicando heterogeneidade, mas o ajuste power‑law feito com método simples não é confiável (alpha estimado ≈ 0.21). Recomendado: usar pacote `powerlaw` para teste estatístico (KS / likelihood).
- Small‑world: sim em termos de distâncias (L ≈ 3.9 e D pequeno) — caminhos curtos característicos de small‑world. Porém, o clustering é baixo (C_avg ≈ 0.027), logo não é um exemplo clássico de WS com clustering alto; é "small‑world" principalmente por curtas distâncias.
- Aleatório (Erdös‑Rényi): improvável. Presença de hubs e assortatividade fortemente negativa não condizem com ER puro. Comparação sintética (arquivo `synthetic_comparison.csv`) mostra ER com L maior e sem hubs tão pronunciados; BA reproduz melhor a existência de hubs.

## Comparação rápida com sintéticos (resumo)
- ER: distâncias maiores e sem hubs pronunciados; métricas no CSV mostram C_avg muito baixo e L ≳ 10.  
- BA: mais próximo em termos de heterogeneidade e caminhos curtos (L menor que ER), mas clustering do BA gerado localmente tende a divergir.  
- WS: com k pequeno gerou grafos pouco conexos / L muito grande no experimento (k=2 nos runs) — não similar ao grafo real para os parâmetros usados.

## Top 3 vértices mais importantes (do script)
- Node 603 — degree = 769, betweenness ≈ 0.55 — hub com papel de ponte entre muitas componentes/aglomerados.  
- Node 1525 — degree = 710, betweenness ≈ 0.43 — hub secundário significativo.  
- Node 288 — degree = 481, betweenness ≈ 0.47 — hub local com alta centralidade de caminho.  
Motivo: altíssimo grau combinado com betweenness elevada indica que esses nós conectam grandes porções da rede e controlam muito do fluxo/alcance.

## Robustez à falhas
- Vulnerabilidade a ataques dirigidos: alto. Remoção progressiva dos maiores graus faz a LCC colapsar rapidamente (arquivo `robustness_lcc_progress.csv` mostra queda pronunciada).  
- Robustez a falhas aleatórias: espera‑se alta (redes com hubs são tipicamente tolerantes a remoções aleatórias), mas recomenda‑se simular remoções aleatórias para confirmar (script adicional sugerido gerou `random_robustness.csv` quando executado).

## Difusão de informação
- Geralmente fácil e rápida enquanto hubs estiverem ativos (curtas distâncias + hubs facilitam alcance amplo). Se hubs forem removidos, difusão piora muito.

## Preservação de informação
- Frágil contra remoções dirigidas: informação centralizada nos hubs tende a perder-se se hubs forem atacados. Em remoções aleatórias, preservação tende a ser melhor.

## Navegabilidade
- Relativamente fácil: presença de hubs e pequenas distâncias facilitam navegação global. Estratégias locais que dependem de alta clustering podem ser menos eficientes devido ao baixo clustering.

## Conclusão prática e próximos passos recomendados
- Para afirmar “scale‑free” com confiança: rodar ajuste com a biblioteca `powerlaw` e obter p‑value / comparação de modelos.  
- Calcular eigenvector centrality na LCC (atualmente eigenvector em todo o grafo retornou 0 no fallback) e comparar topologia local.  
- Rodar teste de robustez aleatória e comparar curvas LCC (dirigida vs aleatória).  
- Incluir CCDF do grau em log‑log com ajuste power‑law no relatório.

```// filepath: