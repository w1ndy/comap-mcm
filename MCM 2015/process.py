import csv, sets, urllib2, json, codecs, time
import networkx as nx
import pygraphviz as pg
import matplotlib.pyplot as plt
import matplotlib.patches as mpat
import random, math

from operator import itemgetter

ignore = ['MALI', 'BOKE', 'CONAKRY', 'TOUGUE', 'KENEMA', 'MONTSERRADO', 'KOINADUGU', 'FARANAH', 'KISSIDOUGO', 'RIVER+GEE', 'LOFA', 'FREETOWN', 'MOYAMBA', 'BOFFA', 'MARGIBI', 'DUBREKA', "N'ZEREKORE", 'FORECARIAH', 'KEROUANE', 'GRAND+GEDEH', 'TONKOLILI', 'MACENTA', 'PITA', 'BONG', 'PUJEHUN', 'KAMBIA', 'COYAH', 'GRAND+CAPE+MOUNT', 'BOMI']
only = ['KOINADUGU']
no_draw = ['KOINADUGU', 'BONTHE', 'GRAND+CAPE+MOUNT', 'BONG']

def get_city_list():
    f = open('data-verbose.csv')
    r = csv.reader(f)
    l = list(r)
    f.close()
    c = sets.Set()
    for row in l[1:]:
        if row[4] != '':
            c.add(row[4].replace(' ', '+') + ',' + row[1].replace(' ', '+'))
    return list(c)

def get_destinations(city):
    return '|'.join(city)

def request(origin, dest):
    url = 'http://maps.googleapis.com/maps/api/distancematrix/json?origins={0}&destinations={1}&language=en-US&sensor=false'.format(origin.replace(' ','+'), dest.replace(' ', '+'))
    print 'Opening url... '
    resp = urllib2.urlopen(url)
    data = resp.read()
    print 'Parsing data...'
    j = json.loads(data)
    if j['status'] != 'OK':
        print 'Status not OK: ' + j['status']
        return
    f = open('distances\\' + origin + '.json', 'w')
    json.dump(j, f)
    f.close()

def go():
    c = get_city_list()
    d = get_destinations(c)
    for i in c:
        if i.split(',')[0] not in ignore and (len(only) == 0 or i.split(',')[0] in only):
            print 'Requesting data for ' + i
            request(i, d)
            print 'Sleeping...'
            time.sleep(10.5)

def test():
    c = get_city_list()
    d = get_destinations(c)
    t = c[0]
    request(t, d)

def generate_matrix(city):
    ret = {c: dict() for c in city}
    for c in city:
        fn = 'distances\\' + c + '.json'
        print 'Parsing ' + fn
        f = open(fn, 'r')
        j = json.loads(f.read())
        for i, n in enumerate(city):
            if j[u'rows'][0][u'elements'][i]['status'] == 'ZERO_RESULTS':
                ret[c][n] = -1
            else:
                ret[c][n] = j[u'rows'][0][u'elements'][i][u'duration'][u'value']
        f.close()
    f = open('distances\\duration_matrix.json', 'w')
    json.dump(ret, f)
    f.close()
    return ret

def read_modularity():
    f = open('modularity.csv')
    c = csv.reader(f)
    l = list(c)[1:]
    modularity = dict()
    for r in l:
        modularity[r[0]] = int(r[1])
    return modularity

def extract_community(G, modularity, num):
    for k in G.nodes():
        if modularity[k] != num:
            G.remove_node(k)

def print_all_community():
    city = get_city_list()
    matrix = generate_matrix(city)
    m = read_modularity()
    for i in range(5):
        G = create_graph(city, matrix)
        extract_community(G, m, i)
        for k in G.nodes():
            print k,
        print '\n'

def find_center():
    city = get_city_list()
    matrix = generate_matrix(city)
    m = read_modularity()
    cases = scan_for_cases()
    case = {}
    for c in cases:
        for k, v in c.iteritems():
            if k in case.keys():
                case[k] += v
            else:
                case[k] = v
    for i in range(5):
        G = create_graph(city, matrix)
        extract_community(G, m, i)
        best = 999999999
        name = ''
        for n1 in G.nodes():
            dist = 0
            for n2 in G.nodes():
                #if n2 in case.keys():
                dist += matrix[n1][n2] * (20 - math.pow(math.e, -0.001  * float(case[n2])))
            if dist < best:
                best = dist
                name = n1
        print i, name

def get_locality(matrix, prev_cases, cases, limit):
    locality, total, rlocality = 0, 0, 0
    for k,v in cases.items():
        total += 100
        if k in prev_cases.keys():
            locality += 100
            rlocality += 100
        else:
            count,rcount,partial,rpartial = 0,0,0,0
            for src in prev_cases:
                s = random.choice(matrix.keys())
                if matrix[s][k] != -1:
                    rcount += 1
                    rpartial += 1.0 - float(matrix[s][k]) / limit
                if matrix[src][k] != -1:
                    count += 1
                    partial += 1.0 - float(matrix[src][k]) / limit
            if count != 0:
                locality += partial * 100 / count
            if rcount != 0:
                rlocality += rpartial * 100 / rcount
    return locality, total, rlocality

def calc_localities():
    city = get_city_list()
    matrix = generate_matrix(city)
    cases = scan_for_cases()

    locality, total, rlocality = [], [], []
    for i, c in enumerate(cases):
        if i != 0:
            l,t,r = get_locality(matrix, cases[i - 1], cases[i], 18000)
            locality.append(l)
            total.append(t)
            rlocality.append(r)
    plt.xlabel('Week Number')
    plt.ylabel('Scaled Value')
    plt.plot(locality, label='Case Locality')
    plt.plot(total, label='Total Cases')
    plt.plot(rlocality, label='Randomly Distributed Case Locality')
    plt.legend(loc=2,prop={'size':10})
    plt.show()

def create_graph(city, matrix, limit = -1, warn = sets.Set(), cases = dict()):
    G = nx.Graph()
    for i in city:
        if i.split(',')[0] not in no_draw:
            if i in warn:
                G.add_node(i,infected=4,vis={'size':cases[i]})
            else:
                G.add_node(i,infected=0)
        else:
            print i + ' is omitted from the graph'
    active_nodes = sets.Set()
    for k,v in matrix.iteritems():
        if k.split(',')[0] not in no_draw:
            for s,t in v.iteritems():
                if k != s and s.split(',')[0] not in no_draw:
                    if t != -1 and (limit == -1 or t < limit):
                        G.add_edge(k,s, weight=(1.0-float(t)/limit)*10)
                        active_nodes.add(k)
                        active_nodes.add(s)
    for i in city:
        if i not in active_nodes and i.split(',')[0] not in no_draw:
            print i + ' is not active'
    return G

def draw_graph(G, fn = 'output.png'):
    G.draw(fn, format='png', prog='neato')

def scan_for_cases():
    f = open('data-verbose.csv')
    r = csv.reader(f)
    l = list(r)
    f.close()
    l = filter(lambda x: x[9] == 'CONFIRMED' and x[4] != '' and x[25] != '',sorted(l[1:], key=itemgetter(15)))
    cases = [dict() for i in range(57)]
    for row in l:
        if row[9] == 'CONFIRMED' and row[4] != '' and row[25] != '':
            y, w = int(row[15][:4]), int(row[15][6:])
            if y == 2014:
                pos = w - 1
            else:
                pos = 51 + w
            district = row[4].replace(' ', '+') + ',' + row[1].replace(' ', '+')
            cases[pos][district] = float(row[25])
    return cases

def create_all_graph():
    city = get_city_list()
    matrix = generate_matrix(city)
    cases = scan_for_cases()
    case = dict()
    for i, elem in enumerate(cases):
        print 'Parsing week #' + str(i) + ', District infected: ' + str(len(case.keys()))
        case = dict(case.items() + elem.items())
        G = create_graph(city, matrix, 18000, case.keys(), case)
        export_nx_to_gephi(G, 'gexf_by_week\\' + str(i / 52 + 2014) + '-' + str(i % 52 + 1) + '.gexf')

def export_nx_to_gephi(G, fn = 'exported.gexf'):
    nx.write_gexf(G, fn)

def export_pg_to_gephi(G, fn = 'exported.gexf'):
    Gn = nx.Graph()
    for n in G.nodes():
        str_attr = dict((str(k), v) for k,v in n.attr.items())
        Gn.add_node(str(n), **str_attr)
    for e in G.edges():
        u,v = str(e[0]), str(e[1])
        attr = dict(e.attr)
        str_attr = dict((str(k),v) for k,v in attr.items())
        Gn.add_edge(u, v, **str_attr)
    nx.write_gexf(Gn, fn)
