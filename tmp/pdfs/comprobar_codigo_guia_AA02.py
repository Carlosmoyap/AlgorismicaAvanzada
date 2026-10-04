from pathlib import Path
import contextlib
import io
import re
from copy import deepcopy
from math import inf
from pypdf import PdfReader

with contextlib.redirect_stdout(io.StringIO()):
    import verificar_AA02 as referencia

base = Path(__file__).resolve().parents[2]
md = Path(__file__).with_name('guia_AA02.md').read_text(encoding='utf-8')
bloques = re.findall(r'```python\n(.*?)```', md, re.S)
funciones = {}
for nombre in ['dfs_iterativo', 'bfs', 'reconstruir', 'componentes', 'flood_fill', 'dijkstra']:
    bloque = next(b for b in bloques if f'def {nombre}(' in b)
    entorno = {}
    exec(compile(bloque, f'guia_{nombre}', 'exec'), entorno)
    funciones[nombre] = entorno[nombre]

assert funciones['dfs_iterativo'](referencia.p10, 'A') == list('ABDEFC')
dist, prev = funciones['bfs'](referencia.p43, 'S')
assert dist == {'A': 1, 'B': 2, 'C': 1, 'D': 1, 'E': 1, 'F': inf, 'G': inf, 'S': 0}
assert funciones['reconstruir'](prev, dist, 'S', 'B') == ['S', 'A', 'B']
assert funciones['reconstruir'](prev, dist, 'S', 'F') is None
assert funciones['reconstruir'](prev, dist, 'S', 'S') == ['S']
numero, ids = funciones['componentes'](referencia.p43)
assert numero == 2 and ids['F'] == ids['G'] != ids['S']
numero, ids = funciones['componentes']({'a': ['b'], 'b': ['a'], 'c': []})
assert numero == 2 and ids['a'] == ids['b'] != ids['c']

cuadricula = [[1, 0, 0, 0], [0, 1, 1, 0], [0, 0, 1, 0], [1, 0, 0, 1]]
imagen = deepcopy(cuadricula)
assert funciones['flood_fill'](imagen, 0, 0, 2) == 1
assert imagen == [[2, 0, 0, 0], [0, 1, 1, 0], [0, 0, 1, 0], [1, 0, 0, 1]]
imagen = deepcopy(cuadricula)
assert funciones['flood_fill'](imagen, 1, 1, 2) == 3
assert funciones['flood_fill'](imagen, 1, 1, 2) == 0
for ocho, esperado in [(False, 4), (True, 2)]:
    pasos = [(df, dc) for df in [-1, 0, 1] for dc in [-1, 0, 1]
             if (df or dc) and (ocho or abs(df) + abs(dc) == 1)]
    adj = {(f, c): [] for f in range(4) for c in range(4) if cuadricula[f][c] == 1}
    for f, c in adj:
        adj[f, c] = [(f + df, c + dc) for df, dc in pasos if (f + df, c + dc) in adj]
    assert funciones['componentes'](adj)[0] == esperado
    assert len(funciones['dfs_iterativo'](adj, (0, 0))) == (5 if ocho else 1)

for grafo, origen, clave in [(referencia.p64, 'a', 'p64_dijkstra'),
                             (referencia.p83, 3, 'p83_dijkstra'),
                             (referencia.p84, 'A', 'p84_dijkstra')]:
    dist, prev = funciones['dijkstra'](grafo, origen)
    assert dist == referencia.r[clave][0]
    assert prev == referencia.r[clave][1]
    for destino in grafo:
        ruta = funciones['reconstruir'](prev, dist, origen, destino)
        assert ruta[0] == origen and ruta[-1] == destino
        coste = sum(dict(grafo[u])[v] for u, v in zip(ruta, ruta[1:]))
        assert coste == dist[destino]

# Zero-cost cycle and disconnected vertex also exercise strict relaxation.
dist, prev = funciones['dijkstra']({'s': [('a', 0)], 'a': [('s', 0)], 'x': []}, 's')
assert dist == {'s': 0, 'a': 0, 'x': inf}
assert prev == {'s': None, 'a': 's', 'x': None}

pdf = base / 'output' / 'pdf' / 'AA02_Explicacion_teoria_y_guia_de_examen.pdf'
lector = PdfReader(pdf)
assert len(lector.pages) == 30
assert len(lector.outline) == 30
assert len(re.findall(r'^@@FIG ', md, re.M)) == 15
print('Verificados: seis bloques de código literales, recorridos, componentes, Flood Fill, tres ejercicios de Dijkstra, rutas y pesos cero. PDF: 30 páginas, 30 marcadores y 15 figuras.')
