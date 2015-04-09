from scholar import *
from BeautifulSoup import BeautifulSoup
from html2text import *
import string
import random
import Queue
import Levenshtein
import urllib2
import networkx as nx
import time
import mechanize
import cookielib
from functools import wraps

def get_random_id(size = 16, chars = string.ascii_letters + string.digits):
	return ''.join(random.choice(chars) for x in range(size))

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

def expand(graph, node, querier, queue):
	print 'database size =', len(G), ', expanding:', G.node[node]['title'], '...'
	keyword = normalize_keyword(G.node[node]['title'])
	querier.query(keyword)
	articles = querier.articles
	found = False
	for art in articles:
		print 'comparing', keyword, 'to', normalize_keyword(art['title']), '...'
		if Levenshtein.ratio(keyword, normalize_keyword(art['title'])) > 0.75:
			found = True
			paper = art
			break
	if not found:
		print 'ERROR unable to locate paper on Google Scholar.'
	else:
		G.node[node]['title'] = paper['title']
		G.node[node]['cited'] = paper['num_citations']
		try:
			url = paper['url_citations']
			if url == None:
				print 'No citation info about this article.\n'
				G.node[node]['expanded'] = True
				return
			start = 0
			#url_opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(querier.cjar))
			#url_opener.addheaders = querier.opener.addheaders
			#url_opener.addheaders = [('Referer', 'http://scholar.google.com/'),('X-Chrome-Variations', 'CPm1yQEIhLbJAQijtskBCKm2yQEIwbbJAQifiMoBCLmIygE='),('Accept-Language', 'zh-CN,zh;q=0.8'),
			#	('Cookie', 'GOOGLE_ABUSE_EXEMPTION=ID=d2deb2c789e0a94c:TM=1391878197:C=c:IP=222.175.103.102-:S=APGng0tGsR0mgzJNJAZqCUM-F7uXx09Rew; GSP=ID=b9657083db1a8b77:LM=1391878202:S=9oSqTxBeH-i_XZ5X; PREF=ID=b9657083db1a8b77:NW=1:TM=1391878202:LM=1391878202:S=QqGF5kwgEwW1hFBF'),
			#	('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.102 Safari/537.36')]
			#url_opener.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.102 Safari/537.36'), ('Cookie', 'SID=DQAAAMoAAABhQfd6tB5FetW-uwbkp0gsaG3tlsSopB0s6rtekVXsvOzUXHf22mPuaI-p4X_xwAK0lwlZ1iuF5HQyAZcobeLOwVvXZE7-uXxP6iV6Faw_iugzGItjV6I3oMV1Ff1ULVsDhqHJeUmBM7fx9GmSwbMGgd-2WW-M8Kvj7xwTXLdLYc9URHfNGm8bIi2hV6Z-TcGoU9bchddNqKZXFEXOWyz5OmnHgrmP-Z4m6mP_ARmPPUOMpc3AiYtyerop5iHK-0tLJyV5BbchwQNl2SWPoqKH;APISID=9HNihsoD6xcM322g/AchuvLJSoh89OT-oP;GSP=ID=f13af891e7ad6846:LM=1391737626:S=kOuPf8vYrYAKj0dC;HSID=AkGRmZDHjUfhwAiM2;NID=67=A8pbI_CPHAqRNmONBzqgQzxQOaRpi4CHFqnaivc-cF-gc0cvoKuCuQqLRfMM291htYS4TtU7tAKKYJui_JAgI2R12wha-J5eHin7BgHA0iU3wpLdfQ5OXav8PTATu_8eClTaMVg7UepHj-S2-50BPyWjapfGG8jH92XDm7i7CWTiVfpjvo30BehE8qAPAHz8UwCUK6u8VkA47ShoFXvKGj0j')]
			while True:
				print 'opening url:', url, 'by offset', start
				t = random.randint(1,5)
				print 'delay',t,'...'
				time.sleep(t)
				cache = ''
				while len(cache) < 80000:
					cache = open_url( url + ('&start=%d' % start)).read()
					print 'fetched length', len(cache)
					if len(cache) < 80000:
						print 'looks like google is doing evil. visit \'%s\' to unlock and update cookie.' % url
						raw_input('press any key to retry...')
						reset()
				soup = BeautifulSoup(cache)
				result = soup.findAll(attrs = {'class': 'gs_rt'})
				print 'got %d result(s) on the page' % len(result)
				for s in result:
					#print 'HTML2Text object constructing...'
					h = HTML2Text()
					#print 'HTML2Text object constructed'
					h.ignore_links = True
					h.body_width = 0
					next_name = h.handle(unicode(s.contents[-1]))
					node_exists = False
					for N, M in nx.get_node_attributes(G, 'title').iteritems():
						if Levenshtein.ratio(unicode(M), unicode(next_name)) > 0.95:
							G.add_edge(N, node)
							if G[N][node]:
								print 'LINK FAILURE'
							print 'DEBUG::EXIST = LINKING', G.node[N]['title'], 'TO', G.node[node]['title']
							node_exists = True
							break
					if node_exists:
						continue
					next_id = get_random_id()
					print 'adding node...'
					priority = int(G.node[node]['priority']) + 1
					G.add_node(
						next_id,
						title = unicode(next_name),
						expanded = False,
						cited = 0,
						priority = priority)
					G.add_edge(next_id, node)
					queue.put((priority, next_id))
				result = soup.findAll(name = 'td', attrs = {'align': 'left'})
				if len(result) == 0:
					if soup.findAll(name = 'img', attrs = {'id': 'recaptcha_logo'}):
						raise Exception('err next page link not found (page imcomplete)')
					else:
						print 'alert: no next page found. may caused by few results.'
						break
				stop_func = False
				for s in result:
					if unicode(s).find(u'visibility:hidden') != -1:
						stop_func = True
						break
				if stop_func:
					break
				start += 10
				t = random.randint(1,5)
				print 'delay',t,'...'
				time.sleep(t)
			G.node[node]['expanded'] = True
		except KeyboardInterrupt, e:
			raise e
		except Exception, what:
			print 'failed to crawl', paper['url_citations']
			print Exception,':',what
	print ''

try:
	G = nx.readwrite.gexf.read_gexf('paper.gexf')
except IOError:
	print 'No history file found, create new graph...'
	G = nx.DiGraph()
	with open('init.set', 'r') as fin:
		paper_title = fin.read().splitlines()
		for t in paper_title:
			G.add_node(
				get_random_id(),
				title = unicode(t),
				expanded = False,
				cited = 0,
				priority = 1)
Q = ScholarQuerier(author='', count=10)
T = Queue.PriorityQueue()
for n, attr in G.nodes(data = True):
	if not attr['expanded']:
		T.put((attr['priority'], n))
try:
	while not T.empty() and len(G) < 100000:
		front = T.get()
		expand(G, front[1], Q, T)
		nx.readwrite.gexf.write_gexf(G, 'paper.gexf')
		cookiejar.save('cookie')
except KeyboardInterrupt:
	print 'Exiting...'
	nx.write_pajek(G, 'paper.net')
	cookiejar.save('cookie')
	exit()