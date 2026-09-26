from pathlib import Path
import re
import html
import json
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Preformatted, Flowable
from reportlab.graphics.shapes import Drawing, Circle, Line, String
from pypdf import PdfReader

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / 'output' / 'pdf'
OUT.mkdir(parents=True, exist_ok=True)
for name, filename in [('Arial', 'arial.ttf'), ('Arial-Bold', 'arialbd.ttf'), ('Arial-Italic', 'ariali.ttf'), ('Consolas', 'consola.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(Path('C:/Windows/Fonts') / filename)))
pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Arial-Bold', italic='Arial-Italic', boldItalic='Arial-Bold')

styles = {
    'body': ParagraphStyle('Body', fontName='Arial', fontSize=10.2, leading=14.1, spaceAfter=7.5, textColor=colors.black),
    'title': ParagraphStyle('Title', fontName='Arial-Bold', fontSize=24, leading=29, spaceAfter=12, textColor=colors.black),
    'h1': ParagraphStyle('H1', fontName='Arial-Bold', fontSize=18, leading=22, spaceAfter=13, textColor=colors.black),
    'h2': ParagraphStyle('H2', fontName='Arial-Bold', fontSize=14, leading=18, spaceBefore=2, spaceAfter=10, textColor=colors.black),
    'h3': ParagraphStyle('H3', fontName='Arial-Bold', fontSize=11.6, leading=15.2, spaceBefore=9, spaceAfter=6, textColor=colors.black),
    'code': ParagraphStyle('Code', fontName='Consolas', fontSize=9.2, leading=12.1, spaceBefore=3, spaceAfter=9, leftIndent=9),
    'cell': ParagraphStyle('Cell', fontName='Arial', fontSize=9.0, leading=11.8),
    'cellhead': ParagraphStyle('CellHead', fontName='Arial-Bold', fontSize=9.0, leading=11.8),
    'list': ParagraphStyle('List', fontName='Arial', fontSize=10.2, leading=14.1, spaceAfter=5, leftIndent=14, firstLineIndent=-14),
    'ref': ParagraphStyle('Ref', fontName='Arial', fontSize=8.7, leading=11.7, spaceBefore=3, spaceAfter=4, textColor=colors.HexColor('#454545')),
}

def inline(text):
    text = html.escape(text)
    subs = dict(zip('₀₁₂₃₄₅₆₇₈₉ᵣ', '0123456789r'))
    sups = dict(zip('⁰¹²³⁴⁵⁶⁷⁸⁹ⁿᵏ⁺⁻', '0123456789nk+-'))
    text = re.sub(r'[₀₁₂₃₄₅₆₇₈₉ᵣ]+', lambda m: '<sub>' + ''.join(subs[c] for c in m[0]) + '</sub>', text)
    text = re.sub(r'[⁰¹²³⁴⁵⁶⁷⁸⁹ⁿᵏ⁺⁻]+', lambda m: '<super>' + ''.join(sups[c] for c in m[0]) + '</super>', text)
    text = re.sub(r'`([^`]+)`', r'<font name="Consolas" size="9.3">\1</font>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
    return text

class Outline(Flowable):
    def __init__(self, key, title):
        Flowable.__init__(self)
        self.key, self.title = key, title
    def wrap(self, aw, ah):
        return 0, 0
    def draw(self):
        self.canv.bookmarkPage(self.key)
        self.canv.addOutlineEntry(self.title, self.key, 0, False)

def diagram(kind):
    width = A4[0] - 42 * mm
    if kind == 'graph':
        d = Drawing(width, 135)
        pos = {'1': (320, 71), '2': (251, 26), '3': (156, 26), '4': (128, 87), '5': (239, 102), '6': (52, 116)}
        edges = [('1','2'),('1','5'),('2','3'),('2','5'),('3','4'),('4','5'),('4','6')]
    else:
        d = Drawing(width, 132)
        pos = {'A':(227,137),'B':(148,100),'C':(306,100),'D':(110,63),'E':(186,63),'F':(306,63),'G':(169,23),'H':(323,23)}
        edges = [('A','B'),('A','C'),('B','D'),('B','E'),('C','F'),('E','G'),('F','H')]
        pos = {key: (x, y*.86) for key, (x, y) in pos.items()}
    for a, b in edges:
        xa, ya = pos[a]; xb, yb = pos[b]
        d.add(Line(xa, ya, xb, yb, strokeWidth=1.3, strokeColor=colors.HexColor('#333333')))
    for label, (x,y) in pos.items():
        d.add(Circle(x,y,12,strokeWidth=1.15,strokeColor=colors.HexColor('#222222'),fillColor=colors.HexColor('#E9F2F8')))
        d.add(String(x,y-4,label,fontName='Arial-Bold',fontSize=11,textAnchor='middle',fillColor=colors.black))
    return d

W = A4[0] - 42 * mm
def make_table(lines):
    rows = [[x.strip() for x in line.strip().strip('|').split('|')] for line in lines]
    cols = len(rows[0])
    if cols == 7:
        widths = [W / 7] * 7
    elif cols == 4:
        widths = [W*.32, W*.225, W*.21, W*.235]
    elif cols == 2:
        widths = [W*.25, W*.75]
    elif rows[0][0] in ['Operación', 'Orden']:
        widths = [W*.29, W*.29, W*.42]
    elif rows[0][0] == 'Bloque':
        widths = [W*.30, W*.13, W*.57]
    elif rows[0][0] == 'Vértice del ejemplo':
        widths = [W*.30, W*.50, W*.20]
    else:
        widths = [W*.30, W*.46, W*.24]
    cells = [[Paragraph(inline(cell), styles['cellhead' if r == 0 else 'cell']) for cell in row] for r,row in enumerate(rows)]
    t = Table(cells, colWidths=widths, repeatRows=1, hAlign='LEFT')
    commands = [
        ('GRID', (0,0), (-1,-1), .5, colors.HexColor('#D9D9D9')),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#DBE8F0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 7), ('RIGHTPADDING',(0,0),(-1,-1),7),
        ('TOPPADDING',(0,0),(-1,-1),5), ('BOTTOMPADDING',(0,0),(-1,-1),5),
    ]
    if cols == 7:
        for row in cells:
            for p in row:
                p.style = ParagraphStyle('MatrixCell', parent=p.style, alignment=TA_CENTER)
    t.setStyle(TableStyle(commands))
    return [Spacer(1,3),t,Spacer(1,10)]

text = (BASE / 'tmp' / 'guia_AA01.md').read_text(encoding='utf-8')
pages = text.split('@@PAGE')
story = []
titles = []
for page_index, page in enumerate(pages):
    if page_index:
        story.append(PageBreak())
    lines = page.strip().splitlines()
    title = lines[0].lstrip('# ').strip()
    titles.append(title)
    story.append(Outline(f'section_{page_index}', title))
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1; continue
        if line.startswith('```'):
            code = []; i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code.append(lines[i]); i += 1
            story.append(Preformatted('\n'.join(code), styles['code']))
            i += 1; continue
        if line.startswith('|'):
            table_lines=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i]); i+=1
            story.extend(make_table(table_lines)); continue
        if line == '@@GRAPH':
            story.append(diagram('graph')); story.append(Spacer(1,6)); i+=1; continue
        if line == '@@TREE':
            story.append(diagram('tree')); story.append(Spacer(1,6)); i+=1; continue
        if line.startswith('# '):
            story.append(Paragraph(inline(line[2:]),styles['title' if page_index==0 else 'h1']))
            i+=1; continue
        if line.startswith('## '):
            story.append(Paragraph(inline(line[3:]),styles['h2'])); i+=1; continue
        if line.startswith('### '):
            story.append(Paragraph(inline(line[4:]),styles['h3'])); i+=1; continue
        if re.match(r'^\d+\. ',line):
            story.append(Paragraph(inline(line),styles['list'])); i+=1; continue
        buf=[line]; i+=1
        while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|','```','@@')):
            buf.append(lines[i].strip()); i+=1
        s=' '.join(buf)
        st='ref' if s.startswith(('Referencia:', 'Referencias:', 'Refuerzo aplicado', 'Refuerzo para practicar', 'Refuerzo de implementación')) else 'body'
        story.append(Paragraph(inline(s),styles[st]))

def decorate(canvas, doc):
    canvas.saveState()
    canvas.setFont('Arial',8)
    canvas.setFillColor(colors.HexColor('#555555'))
    if doc.page > 1:
        canvas.drawString(21*mm,A4[1]-15*mm,'Teoría 1  |  Complejidad y fundamentos de grafos')
    canvas.drawString(21*mm,14*mm,'Algorísmica Avanzada  ·  AA01')
    canvas.drawRightString(A4[0]-21*mm,14*mm,str(doc.page))
    canvas.restoreState()

path = OUT / 'AA01_Explicacion_teoria_y_guia_de_examen.pdf'
doc = SimpleDocTemplate(str(path),pagesize=A4,rightMargin=21*mm,leftMargin=21*mm,topMargin=23*mm,bottomMargin=21*mm,
    title='Teoría 1 de Algorísmica Avanzada',author='Guía de estudio',subject='Complejidad y fundamentos de grafos explicados a partir de AA01')
doc.build(story,onFirstPage=decorate,onLaterPages=decorate)
reader=PdfReader(path)
mapping=[]
for i,p in enumerate(reader.pages):
    extracted=p.extract_text()
    mapping.append({'pagina':i+1,'primeras_lineas':extracted.splitlines()[:5],'caracteres':len(extracted)})
report={'output':str(path),'paginas':len(reader.pages),'paginas_planeadas':len(pages),'titulos':titles,'mapeo':mapping}
(BASE/'tmp'/'AA01_verificacion.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
