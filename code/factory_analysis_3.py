# set the matplotlib backend so figures can be saved in the background
import matplotlib
matplotlib.use("Agg")
# import the necessary packages
import sys
import argparse
import numpy as np
from igraph import *
import seaborn as sns
import matplotlib.pyplot as plt
from model_gen import ModelGenerator
from model_gen import ModelGeneratorNS
from model_gen import DynamicManufacturing

# analysis of alpha (# steps/# machines) for the stationary period

# argument parser
ap = argparse.ArgumentParser()
ap.add_argument("-n", "--nodes", type=int, default=500)
#ap.add_argument("-s", "--production_steps", type=int, default=300)
ap.add_argument("-p", "--first_step", type=int, default=-1)
ap.add_argument("-l", "--last_step", type=int, default=-1)
ap.add_argument("-b", "--buffer_size", type=int, default=1)
ap.add_argument("-f", "--failure_rate", type=float, default=0.1)
ap.add_argument("-t", "--production", default="constant")
ap.add_argument("-i", "--samples", type=int, default=30)
ap.add_argument("-e", "--seed", type=int, default=42) 
ap.add_argument("-o", "--output", default="-")
ap.add_argument("-r", "--iterations", type=int, default=1000) 
ap.add_argument("-d", "--delta", type=float, default=0.1) 
args = vars(ap.parse_args())

# list of nodes to vary the algorithm
#nodes_list = [3000, 1500, 1000, 750, 600, 500, 429, 375, 334, 300]
psteps_list = [25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 275, 300, 325, 350, 375, 400, 425, 450, 475, 500]
#psteps_list = [50, 75, 100, 125, 150, 175, 200, 225, 250, 275, 300, 325, 350, 375, 400, 425, 450, 475, 500]
# our control variable is alpha
# number of production steps / number of machines
alpha = []

starved_aggregated = []
blocked_aggregated = []
working_aggregated = []
starved_nodes = np.zeros((args["samples"]))
blocked_nodes = np.zeros((args["samples"]))
working_nodes = np.zeros((args["samples"]))

#state_array = np.zeros((args["samples"], args["iterations"], args["production_steps"]))

with open("output/" + args["output"] + "_aggregated_info.txt", 'w') as f2:
   	f2.write("production_steps,nodes,starved_nodes,blocked_nodes,working_nodes,alpha\n")

for psteps in psteps_list:

	print("[INFO] Number of production steps selected {}...".format(psteps))

	for s in range(args["samples"]):

		output_file = "output/" + args["output"] + "_nodes{}_ptep{}_sample{}.txt".format(args["nodes"], psteps, s)

		print("[INFO] Generating graph instance {}...".format(s))

		mg = ModelGeneratorNS(n=args["nodes"], s=psteps, 
			first_step=args["first_step"], last_step=args["last_step"], failure_rate=args["failure_rate"], 
			buffer_size=args["buffer_size"], production_level=args["production"], production_delta=args["delta"])

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
				#if runs < (args["iterations"]-100): # log last 100 iterations
				#	stable_nodes  = system.iterate(f, False)
				#else:
				# 0 -> starved / 1 -> blocked / 2 -> working
				production, zero_count, one_count, two_count, _ = system.iterate(f, True)
				#print("{}-{}-{}-{}".format(production,zero_count,one_count,two_count))

				runs = runs + 1

				if (psteps < 250):
					if (runs%1==0):
						print("[INFO] run: {}".format(runs))
				else:
					if (runs%100==0):
						print("[INFO] run: {}".format(runs))

		# store the normalized number of working machines/nodes of the last iteration
		starved_nodes[s] = zero_count/args["nodes"]
		blocked_nodes[s] = one_count/args["nodes"]
		working_nodes[s] = two_count/args["nodes"]

	# take the mean of the working nodes per sample and put it
	# in the list of working nodes aggregated
	starved_aggregated.append(np.average(starved_nodes, axis=0))
	blocked_aggregated.append(np.average(blocked_nodes, axis=0))
	working_aggregated.append(np.average(working_nodes, axis=0))
	# append the respective alpha
	alpha.append(psteps/args["nodes"])

	print("[INFO] Write to file...")

	with open("output/" + args["output"] + "_aggregated_info.txt", 'a') as f2:
		#f2.write("production_steps,nodes,starved_nodes,blocked_nodes,working_nodes,alpha\n")
		f2.write("{},{},{},{},{},{}\n".format(psteps,args["nodes"],starved_aggregated[-1],blocked_aggregated[-1],working_aggregated[-1],alpha[-1]))

plt.style.use("ggplot")
plt.figure()
plt.plot(alpha, working_aggregated)
plt.ylabel("% Working Machines")
plt.xlabel("Alpha (production steps/machines)")
plt.savefig("output/alpha.png")
