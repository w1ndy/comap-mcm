import networkx as nx
import redis
import re

srv = redis.Redis(host='127.0.0.1')
firstline = True
artist = re.compile('^(.+)\t')
movie = re.compile('\t+(.*)\s+\(\d\d\d\d')
last_node = ''
cnt = 0

with open('actors.list') as f:
	for line in f:
		if len(line) < 2:
			firstline = True
			print ''
			continue
		if firstline:
			r = artist.search(line)
			if not r:
				print 'ARTIST MATCH ERROR:', line
			else:
				last_node = r.group(1).strip(' \n\r\t"')
				print cnt, 'COLLECTED'
				print 'LIST BEGIN:', last_node
				firstline = False
				cnt = 0
		if not firstline:
			r = movie.search(line)
			if not r:
				print 'MOVIE MATCH ERROR:', line
			else:
				title = r.group(1).strip(' \n\r\t"(<{}>)')
				srv.sadd(title, last_node)
				cnt += 1
				#print 'ADD MOVIE:', title
