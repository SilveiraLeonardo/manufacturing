import sys
import argparse
import numpy as np
from igraph import *
from model_gen import ModelGenerator
from model_gen import ModelGeneratorNS
from model_gen import DynamicManufacturing

# argument parser
ap = argparse.ArgumentParser()
ap.add_argument("-n", "--nodes", type=int, default=450)
ap.add_argument("-s", "--production_steps", type=int, default=300)
ap.add_argument("-f", "--first_step", type=int, default=-1)
ap.add_argument("-l", "--last_step", type=int, default=-1)
ap.add_argument("-b", "--buffer_size", type=int, default=10)
ap.add_argument("-i", "--samples", type=int, default=25)
ap.add_argument("-e", "--seed", type=int, default=42) 
ap.add_argument("-o", "--output", default="-")
ap.add_argument("-r", "--iterations", type=int, default=1000) 
args = vars(ap.parse_args())

for s in range(args["samples"]):

	output_file = args["output"] + "_{}.txt".format(s)

	print("[INFO] Generating graph instance {}...".format(s))

	mg = ModelGeneratorNS(n=args["nodes"], s=args["production_steps"], 
		first_step=args["first_step"], last_step=args["last_step"], buffer_size=args["buffer_size"])

	#ws, edges, edge_attr, vertex_attr = mg.generate_graph()
	ws, edges, vertex_attr = mg.generate_graph()

	g = Graph(n=args["nodes"], edges=edges, directed=True,
					vertex_attrs=vertex_attr)

	assert(g.is_dag())

	print("[INFO] Starting dynamic model...")
	system = DynamicManufacturing(g, args["seed"])

	# run the dynamic simulation and output the results to the defined medium
	with sys.stdout if args["output"] == "-" else open(output_file, "w") as f:
		runs = 0
		while runs < args["iterations"]:
			if runs < (args["iterations"]-100): # log last 100 iterations
				production  = system.iterate(f, False)
			else:
				production  = system.iterate(f, True)

			runs = runs + 1
			if (runs%100==0):
				print("[INFO] run: {}".format(runs))


