from math import hypot
from reportlab.graphics.shapes import Drawing, Circle, Line, String, Polygon, Rect, Ellipse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

W=A4[0]-42*mm
INK=colors.HexColor('#263746')
BLUE=colors.HexColor('#136695')
PALE=colors.HexColor('#E8F2F8')
GREEN=colors.HexColor('#DCEEDB')
WHITE=colors.white

def label(d,x,y,s,size=10,bold=False,color=INK,anchor='middle'):
    d.add(String(x,y,str(s),fontName='Arial-Bold' if bold else 'Arial',fontSize=size,fillColor=color,textAnchor=anchor))

def edge(d,a,b,directed=False,weight=None,labelpos=None,color=INK,width=1.3,r=12,offset=0):
    x1,y1=a;x2,y2=b;length=hypot(x2-x1,y2-y1);dx=(x2-x1)/length;dy=(y2-y1)/length
    px,py=-dy,dx
    sx,sy=x1+r*dx+offset*px,y1+r*dy+offset*py
    ex,ey=x2-r*dx+offset*px,y2-r*dy+offset*py
    d.add(Line(sx,sy,ex,ey,strokeColor=color,strokeWidth=width))
    if directed:
        d.add(Polygon([ex,ey,ex-6*dx+2.8*px,ey-6*dy+2.8*py,ex-6*dx-2.8*px,ey-6*dy-2.8*py],fillColor=color,strokeColor=color,strokeWidth=.3))
    if weight is not None:
        lx,ly=labelpos or ((x1+x2)/2+10*px,(y1+y2)/2+10*py)
        d.add(Rect(lx-9,ly-3,18,14,fillColor=WHITE,strokeColor=None))
        label(d,lx,ly,weight,10,bold=True)

def nodes(d,pos,fill=PALE,r=12,selected=()):
    for u,(x,y) in pos.items():
        d.add(Circle(x,y,r,fillColor=GREEN if u in selected else fill,strokeColor=INK,strokeWidth=1.2))
        label(d,x,y-3.6,u,10.4,True)

def graph(pos,edges,height,directed=False,weights=None,labelpositions=None,selected=()):
    d=Drawing(W,height)
    for i,(a,b) in enumerate(edges):
        edge(d,pos[a],pos[b],directed,weights[i] if weights else None,(labelpositions or {}).get((a,b)))
    nodes(d,pos,selected=selected)
    return d

def diagram(kind):
    if kind=='recorridos':
        return graph({'A':(120,95),'B':(50,28),'C':(190,28),'D':(355,95)},[('A','B'),('B','C'),('C','A'),('A','D')],120)
    if kind=='dfs_original':
        return graph({'A':(75,100),'B':(205,100),'C':(75,25),'D':(345,115),'E':(345,55),'F':(205,25)},[('A','B'),('A','C'),('B','D'),('B','E'),('C','F'),('E','F')],140,True)
    if kind=='dfs_arbol':
        return graph({'A':(235,122),'B':(170,86),'C':(325,86),'D':(115,48),'E':(225,48),'F':(225,12)},[('A','B'),('A','C'),('B','D'),('B','E'),('E','F')],146,True)
    if kind=='ejercicio43':
        pos={'E':(60,100),'S':(180,100),'A':(300,100),'F':(410,100),'D':(60,25),'C':(180,25),'B':(300,25),'G':(410,25)}
        return graph(pos,[('E','S'),('S','A'),('E','D'),('D','S'),('S','C'),('D','C'),('C','B'),('A','B'),('F','G')],125)
    if kind=='comparacion_arboles':
        d=Drawing(W,92)
        label(d,110,80,'Árbol DFS',10.5,True);label(d,355,80,'Árbol BFS',10.5,True)
        p={u:(20+i*39,43) for i,u in enumerate('SABCDE')}
        for a,b in zip('SABCD','ABCDE'):edge(d,p[a],p[b],True,r=10)
        nodes(d,p,r=10)
        p={'S':(355,57),'A':(285,28),'C':(330,28),'D':(377,28),'E':(422,28),'B':(285,3+8)}
        # B goes below A without overlapping its circle.
        p['A']=(277,38);p['B']=(259,12)
        for a,b in [('S','A'),('S','C'),('S','D'),('S','E'),('A','B')]:edge(d,p[a],p[b],True,r=9)
        nodes(d,p,r=9)
        return d
    if kind=='componentes':
        d=Drawing(W,119)
        for x,y,rx,ry in [(105,70,92,45),(304,70,65,33),(420,70,28,33)]:
            d.add(Ellipse(x,y,rx,ry,fillColor=colors.HexColor('#F2F6F8'),strokeColor=colors.HexColor('#BCCDD6'),strokeWidth=.7))
        pos={'A':(48,56),'B':(107,93),'C':(163,56),'D':(278,70),'E':(330,70),'F':(420,70)}
        for a,b in [('A','B'),('B','C'),('D','E')]:edge(d,pos[a],pos[b])
        nodes(d,pos);label(d,105,8,'Componente 1');label(d,304,8,'Componente 2');label(d,420,8,'Aislado')
        return d
    if kind=='componentes_dirigidas':
        d=Drawing(W,160)
        for x,y,rx,ry in [(98,95,80,52),(285,95,66,37),(415,95,28,37)]:
            d.add(Ellipse(x,y,rx,ry,fillColor=colors.HexColor('#F2F6F8'),strokeColor=colors.HexColor('#BCCDD6'),strokeWidth=.7))
        pos={'A':(43,85),'B':(98,133),'C':(153,85),'D':(251,95),'E':(319,95),'F':(415,95)}
        for a,b in [('A','B'),('B','C'),('C','A'),('C','D'),('E','F')]:edge(d,pos[a],pos[b],True)
        edge(d,pos['D'],pos['E'],True,offset=5);edge(d,pos['E'],pos['D'],True,offset=5)
        nodes(d,pos)
        label(d,98,21,'{A, B, C}');label(d,285,21,'{D, E}');label(d,415,21,'{F}')
        return d
    if kind=='flood':
        d=Drawing(W,170);grid=[[1,0,0,0],[0,1,1,0],[0,0,1,0],[1,0,0,1]]
        for ox,name,selected in [(65,'Conectividad 4',{(0,0)}),(291,'Conectividad 8',{(0,0),(1,1),(1,2),(2,2),(3,3)})]:
            label(d,ox+54,154,name,11,True)
            for f in range(4):
                for c in range(4):
                    x,y=ox+c*27,118-f*27
                    fill=GREEN if (f,c) in selected else (PALE if grid[f][c] else WHITE)
                    d.add(Rect(x,y,27,27,fillColor=fill,strokeColor=colors.HexColor('#AAAAAA'),strokeWidth=.65))
                    label(d,x+13.5,y+9,grid[f][c],11,(f,c) in selected)
            label(d,ox+54,18,str(len(selected))+' celda'+('s' if len(selected)>1 else '')+' alcanzada'+('s' if len(selected)>1 else ''),10)
        label(d,W/2,3,'Verde indica la región alcanzada desde la esquina superior izquierda',9)
        return d
    if kind=='expansion':
        d=Drawing(W,152)
        p={'A':(60,113),'B':(415,113)}
        edge(d,p['A'],p['B'],True,3,(238,127));nodes(d,p)
        label(d,238,93,'Arista original de peso 3',10)
        p={'A':(60,42),'x':(178,42),'y':(296,42),'B':(415,42)}
        for a,b in [('A','x'),('x','y'),('y','B')]:edge(d,p[a],p[b],True,1)
        nodes(d,p);label(d,238,4,'Dos vértices nuevos y tres pasos unitarios',10)
        return d
    if kind=='negativo':
        pos={'S':(80,93),'A':(355,93),'B':(245,23)}
        return graph(pos,[('S','A'),('S','B'),('B','A')],121,True,[2,5,-4],{('S','A'):(214,104),('S','B'):(146,51),('B','A'):(316,48)})
    if kind=='heap':
        d=Drawing(W,146)
        pos={0:(W/2,126),1:(W/2-86,86),2:(W/2+86,86),3:(W/2-126,28),4:(W/2-46,28),5:(W/2+46,28),6:(W/2+126,28)}
        for a,b in [(0,1),(0,2),(1,3),(1,4),(2,5),(2,6)]:edge(d,pos[a],pos[b],r=15)
        values=[10,15,30,40,50,100,40]
        for u,(x,y) in pos.items():
            d.add(Circle(x,y,15,fillColor=PALE,strokeColor=INK,strokeWidth=1.2));label(d,x,y-3.5,values[u],10.3,True)
        return d
    if kind in ['dijkstra_original','dijkstra_arbol']:
        pos={'a':(40,82),'b':(145,137),'c':(145,27),'d':(301,137),'e':(301,27),'z':(425,82)}
        edges=[('a','b'),('a','c'),('b','c'),('b','d'),('c','d'),('c','e'),('d','e'),('d','z'),('e','z')]
        weights=[4,2,1,5,8,10,2,6,5]
        lp={('a','b'):(89,121),('a','c'):(83,46),('b','c'):(128,82),('b','d'):(223,149),('c','d'):(232,92),('c','e'):(223,39),('d','e'):(319,82),('d','z'):(370,123),('e','z'):(369,46)}
        if kind=='dijkstra_arbol':
            edges=[('a','c'),('c','b'),('b','d'),('d','e'),('d','z')];weights=[2,1,5,2,6]
            lp[('c','b')]=(128,82)
        return graph(pos,edges,166,kind=='dijkstra_arbol',weights,lp)
    if kind=='ejercicio83':
        pos={'1':(102,19),'2':(45,93),'3':(206,92),'4':(133,162),'5':(325,130),'6':(390,23),'7':(357,191)}
        es=[('4','2'),('4','3'),('4','7'),('2','3'),('2','1'),('1','3'),('3','5'),('3','6'),('5','7'),('5','6')]
        ws=[2,7,1,4,8,1,5,12,4,6]
        lp={('4','2'):(78,137),('4','3'):(183,137),('4','7'):(244,192),('2','3'):(124,105),('2','1'):(58,51),('1','3'):(163,46),('3','5'):(263,124),('3','6'):(303,47),('5','7'):(348,159),('5','6'):(366,83)}
        return graph(pos,es,215,False,ws,lp,selected=('3',))
    if kind=='ejercicio84':
        pos={'A':(40,130),'B':(170,130),'C':(300,130),'D':(430,130),'E':(40,22),'F':(170,22),'G':(300,22),'H':(430,22)}
        es=[('A','B'),('B','C'),('C','D'),('A','E'),('A','F'),('B','F'),('B','G'),('C','G'),('D','G'),('D','H'),('E','F'),('G','F'),('G','H')]
        ws=[1,2,1,4,8,6,6,2,1,4,5,1,1]
        lp={('A','B'):(105,141),('B','C'):(235,141),('C','D'):(365,141),('A','E'):(23,76),('A','F'):(116,76),('B','F'):(153,76),('B','G'):(246,76),('C','G'):(283,76),('D','G'):(373,76),('D','H'):(446,76),('E','F'):(105,34),('G','F'):(235,7),('G','H'):(365,34)}
        return graph(pos,es,161,True,ws,lp,selected=('A',))
    raise ValueError(kind)
