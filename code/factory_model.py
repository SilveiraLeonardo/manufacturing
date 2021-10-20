import sys
import argparse
import numpy as np
from igraph import *
from model_gen import ModelGenerator
from model_gen import ModelGeneratorNS
from model_gen import DynamicManufacturing

# argument parser
ap = argparse.ArgumentParser()
ap.add_argument("-n", "--nodes", required=True, type=int)
ap.add_argument("-s", "--production_steps", required=True, type=int)
ap.add_argument("-f", "--first_step", type=int, default=-1)
ap.add_argument("-l", "--last_step", type=int, default=-1)
ap.add_argument("-r", "--seed", required=True, type=int) 
ap.add_argument("-o", "--output", required=True, default="-")
args = vars(ap.parse_args())

print("[INFO] Generating graph...")

mg = ModelGeneratorNS(n=args["nodes"], s=args["production_steps"], 
	first_step=args["first_step"], last_step=args["last_step"])

#ws, edges, edge_attr, vertex_attr = mg.generate_graph()
ws, edges, vertex_attr = mg.generate_graph()

g = Graph(n=args["nodes"], edges=edges, directed=True,
				vertex_attrs=vertex_attr)

assert(g.is_dag())

# drawing graphs
layout = g.layout("kamada_kawai")
plot(g, layout=layout)

print("[INFO] Starting dynamic model...")
system = DynamicManufacturing(g, args["seed"])

# run the dynamic simulation and output the results to the defined medium
with sys.stdout if args["output"] == "-" else open(args["output"], "w") as f:
	production = 0
	runs = 0
	while production < 100:
		print("[INFO] run: {}".format(runs))
		production = production + system.iterate(f)
		runs = runs + 1
