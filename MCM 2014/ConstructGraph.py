import networkx as nx
import networkx.drawing.nx_pydot as nxdot

name = []
G = nx.MultiGraph()
with open('name.in') as fname:
	tmp = fname.read().splitlines()
	name = tmp
	for n in name:
		G.add_node(n)
print name;
p = 0;
with open('graph.in') as fgraph:
	for line in fgraph:
		array = [int(x) for x in line.split()]
		for x in array:
			G.add_edge(name[p], name[x])
		p += 1
print(G.edges())
nx.readwrite.gml.write_gml(G, 'graph.gml')
nxdot.write_dot(G, 'graph.dot')
