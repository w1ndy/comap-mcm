import re
import networkx as nx
import codecs

with open('data.in') as f:
	data = f.read().splitlines()

G = nx.Graph()
for author in data:
	if author and author[0] != '\t':
		result = re.match('(.*[a-zA-Z0-9).*])\s\s+([0-9]+):?\s*([0-9]*)', author)
		if result:
			times = 1 if not result.group(3) else result.group(3)
			G.add_node(result.group(1), isCore=1)

for author in data:
	if author:
		if author[0] != '\t':
			result = re.match(
				'(.*[a-zA-Z0-9).*])\s\s+([0-9]+):?\s*([0-9]*)',
				author)
			if result:
				last_str = result.group(1)
		else:
			name = author[1:]
			if name.isupper():
				G.add_edge(last_str, name, weight=1, isCore=1)
			else:
				G.add_edge(last_str, name, weight=1, isCore=0)

print 'Calculating betweenness centrality...'
Bc = nx.algorithms.centrality.betweenness_centrality(G)
print 'Calculating degree centrality...'
Dc = nx.algorithms.centrality.degree_centrality(G)
print 'Calculating pagerank...'
Pr = nx.algorithms.link_analysis.pagerank_alg.pagerank(G)
print 'Calculating eigenvector centrality...'
Ec = nx.algorithms.centrality.eigenvector_centrality(G)

nx.set_node_attributes(G, 'degree_centrality',
	{k: '%.6f' % v for k, v in Dc.items()})
nx.set_node_attributes(G, 'pagerank',
	{k: '%.6f' % v for k, v in Pr.items()})
nx.set_node_attributes(G, 'eigenvector_centrality',
	{k: '%.6f' % v for k, v in Ec.items()})
nx.set_node_attributes(G, 'betweenness_centrality',
	{k: '%.6f' % v for k, v in Bc.items()})

nx.readwrite.gml.write_gml(G, 'Gfinal.gml')
