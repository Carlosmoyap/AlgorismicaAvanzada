from collections import deque
from heapq import heappop, heappush
from math import inf
from itertools import count
import json
from pathlib import Path

def graph(vertices,edges,directed=False):
    g={u:[] for u in vertices}
    for edge in edges:
        u,w,*weight=edge
        g[u].append((w,weight[0]) if weight else w)
        if not directed: g[w].append((u,weight[0]) if weight else u)
    for u in g: g[u].sort()
    return g

def dfs(g,s):
    seen=set(); out=[]; parent={s:None}; events=[]
    def visit(u):
        seen.add(u); out.append(u)
        for w in g[u]:
            if w not in seen:
                parent[w]=u; visit(w)
    visit(s)
    return out,parent

def bfs(g,s):
    dist={s:0}; prev={s:None}; q=deque([s]); out=[]; trace=[('inicio',list(q))]
    while q:
        u=q.popleft();out.append(u)
        for w in g[u]:
            if w not in dist:
                dist[w]=dist[u]+1;prev[w]=u;q.append(w)
        trace.append((u,list(q)))
    return out,dist,prev,trace

def dijkstra(g,s):
    dist={u:inf for u in g};prev={u:None for u in g};dist[s]=0; q=[(0,s)]; trace=[]
    while q:
        du,u=heappop(q)
        if du!=dist[u]:continue
        for w,c in g[u]:
            if du+c<dist[w]:dist[w]=du+c;prev[w]=u;heappush(q,(dist[w],w))
        trace.append({'fijado':u,'dist':dist.copy(),'prev':prev.copy()})
    return dist,prev,trace

p10={'A':['B','C'],'B':['D','E'],'C':['F'],'D':[],'E':['F'],'F':[]}
p43=graph('ABCDEFGS',[('E','S'),('S','A'),('E','D'),('D','S'),('S','C'),('D','C'),('C','B'),('A','B'),('F','G')])
p64=graph('abcdez',[('a','b',4),('a','c',2),('b','c',1),('b','d',5),('c','d',8),('c','e',10),('d','e',2),('d','z',6),('e','z',5)])
p83=graph(range(1,8),[(4,2,2),(4,3,7),(4,7,1),(2,3,4),(2,1,8),(1,3,1),(3,5,5),(3,6,12),(5,7,4),(5,6,6)])
p84=graph('ABCDEFGH',[('A','B',1),('B','C',2),('C','D',1),('A','E',4),('A','F',8),('B','F',6),('B','G',6),('C','G',2),('D','G',1),('D','H',4),('E','F',5),('G','F',1),('G','H',1)],True)

def contains(items,x,counters):
    counters['tests']+=1
    for y in items:
        counters['comparisons']+=1
        if y==x:return True
    return False

def original_iterative_complete(n):
    g={u:[w for w in range(n) if w!=u] for u in range(n)}
    seen=[];stack=[0];stats={'tests':0,'comparisons':0,'pops':0,'neighbor_scans':0}
    while stack:
        u=stack.pop();stats['pops']+=1
        if not contains(seen,u,stats):seen.append(u)
        for w in g[u]:
            stats['neighbor_scans']+=1
            if not contains(seen,w,stats):stack.append(w)
    return stats

r={'p10_dfs':dfs(p10,'A'),'p43_dfs':{s:dfs(p43,s) for s in p43},'p43_bfs':bfs(p43,'S'),
   'p64_dijkstra':dijkstra(p64,'a'),'p83_dijkstra':dijkstra(p83,3),'p84_dijkstra':dijkstra(p84,'A'),
   'p11_dense_counts':{n:original_iterative_complete(n) for n in [8,16,32,64]}}
assert r['p10_dfs'][0]==list('ABDEFC')
assert r['p43_bfs'][0]==list('SACDEB')
assert r['p64_dijkstra'][0]=={'a':0,'b':3,'c':2,'d':8,'e':10,'z':14}
assert r['p83_dijkstra'][0]=={1:1,2:4,3:0,4:6,5:5,6:11,7:7}
assert r['p84_dijkstra'][0]=={'A':0,'B':1,'C':3,'D':4,'E':4,'F':6,'G':5,'H':6}
Path(__file__).with_name('AA02_ejemplos_verificados.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(r,ensure_ascii=False,indent=2))
