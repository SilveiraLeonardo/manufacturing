import numpy as np
from igraph import *
from model_gen import ModelGenerator

# parâmetros do modelo
n = 20 # numero de nós
s = 0.2 # serialidade da rede. Valores no intervalo [0, 1]
# s=0.0: rede totalmente paralela (todos os nós em paralelo)
# s=1.0: rede totalmente serial (todos os nós em série)

mg = ModelGenerator(n=n, s=s)

ws, edges, edge_attr, vertex_attr = mg.generate_graph()

print(ws)
print(edges)
print(edge_attr)
print(vertex_attr)

g = Graph(n=n, edges=edges, directed=True,
          edge_attrs=edge_attr,
          vertex_attrs=vertex_attr)

summary(g)

# drawing graphs
layout = g.layout("kamada_kawai")
plot(g, layout=layout)
