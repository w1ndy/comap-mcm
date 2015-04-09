from scholar import *
import networkx as nx
import Levenshtein

def normalize_keyword(title):
	if isinstance(title, str):
		title = unicode(title)
	not_letters = u'0123456789!"#%\'()*+,-./:;<=>?@[\]^_`{|}~'
	translate_table = dict((ord(char), u' ') for char in not_letters)
	raw = title.translate(translate_table)
	raw = raw.lower()
	prev = u' '
	result = u''
	for ch in raw:
		if ch != prev or ch != u' ':
			result += ch
			prev = ch
	return result

G = nx.readwrite.gexf.read_gexf('paper.gexf')
priority = nx.get_node_attributes(G, 'priority')

querier = ScholarQuerier('', 10)
count = 0
for K, V in priority.iteritems():
	count += 1
	if V > 1:
		keyword = normalize_keyword(G.node[K]['title'])
		print '\n',count,'of',len(G),'SEARCHING', keyword, '...'
		skip = False
		while not skip:
			try:
				querier.query(str(keyword))
			except UnicodeEncodeError, e:
				print 'UNICODE ENCODE ERROR SKIPPED'
				G.node[K]['cited'] = 0
				skip = True
			except Exception, e:
				print 'ERROR:', e
				G.node[K]['cited'] = 0
				s = raw_input('press enter to retry or s to skip...')
				if 's' in s:
					skip = True
			else:
				break
		if skip:
			continue
		found = False
		for art in querier.articles:
			if Levenshtein.ratio(keyword, normalize_keyword(art['title'])) > 0.75:
				G.node[K]['cited'] = 0 if not art['num_citations'] else art['num_citations']
				print 'FOUND MATCH', art['title'], 'NUM_CITATION', art['num_citations']
				found = True
				break
		if not found:
			print 'NO MATCHING RESULT'
		else:
			nx.readwrite.gexf.write_gexf(G, 'paper.gexf')
