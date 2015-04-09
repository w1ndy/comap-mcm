import re
import matplotlib.pyplot as plt

def parse_cases_deaths():
    f = open('data_healthmap.html')
    data = f.read()
    matcher = re.compile('<li.*?>|</li.*?>', re.S | re.I)
    last, layer, ret = 0, 0, []
    for b in matcher.finditer(data):
        if b.group(0)[1] != '/':
            if layer == 0:
                last = b.start()
            layer += 1
        else:
            layer -= 1
            if layer == 0:
                ret.append(data[last:b.end()])
    ft = re.compile('casecounts">(.*?) <span class="cases">(\\d+) case(?:s)?</span>(?:\\s*<span class="deaths">(\\d+) death(?:s)?)?', re.S | re.I)
    cases, deaths = [], []
    for i, s in zip(range(len(ret)), ret):
        cases.append(dict())
        deaths.append(dict())
        for m in ft.finditer(s):
            cases[i][m.group(1)] = int(0 if m.group(2) is None else m.group(2))
            deaths[i][m.group(1)] = int(0 if m.group(3) is None else m.group(3))
    for d in cases:
        t = 0
        for i in d.itervalues():
            t += i
        d['Total'] = t
    for d in deaths:
        t = 0
        for i in d.itervalues():
            t += i
        d['Total'] = t
    return cases, deaths

def draw_total(cases, deaths):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    points = []
    for d in cases:
        points.append(d['Total'] if d['Total'] != 0 or len(points) == 0 else points[-1])
    ax.plot(points)
    bx = fig.add_subplot(111)
    points = []
    for d in deaths:
        points.append(d['Total'] if d['Total'] != 0 or len(points) == 0 else points[-1])
    bx.plot(points)
    fig.show()

