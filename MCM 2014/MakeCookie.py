import sys

if len(sys.argv) != 2:
	print 'usage: %s COOKIE' % sys.argv[0]
	exit()
l = sys.argv[1].split(';')
f = open('cookie', 'w')
f.write('#LWP-Cookies-2.0\n')
for x in l:
	f.write('Set-Cookie3: %s; ; path="/"; domain=".google.com"; path_spec; domain_dot; expires="2016-01-01 00:00:00Z"; version=0\n' % x)
f.close()
