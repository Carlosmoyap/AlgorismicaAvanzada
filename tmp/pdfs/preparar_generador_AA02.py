from pathlib import Path
base=Path(__file__).resolve().parents[2]
s=(base/'tmp'/'crear_guia_AA01.py').read_text(encoding='utf-8')
s=s.replace('BASE = Path(__file__).resolve().parent.parent','BASE = Path(__file__).resolve().parents[2]')
s=s.replace('AA01','AA02').replace('Teoría 1','Teoría 2').replace('Complejidad y fundamentos de grafos','Recorridos componentes y caminos mínimos')
s=s.replace("BASE / 'tmp' / 'guia_AA02.md'","BASE / 'tmp' / 'pdfs' / 'guia_AA02.md'")
a=s.index('def diagram(kind):');b=s.index('W = A4[0] - 42 * mm',a)
s=s[:a]+'from aa02_figuras import diagram\n\n'+s[b:]
s=s.replace('if cols == 7:','if cols >= 5:').replace('widths = [W / 7] * 7','widths = [W / cols] * cols')
s=s.replace("if line == '@@GRAPH':","if line.startswith('@@FIG '):\n            story.append(diagram(line.split()[1])); story.append(Spacer(1,6)); i+=1; continue\n        if line == '@@GRAPH':")
s=s.replace("(BASE/'tmp'/'AA02_verificacion.json')","(BASE/'tmp'/'pdfs'/'AA02_verificacion.json')")
s=s.replace("title='Teoría 2 de Algorísmica Avanzada'","title='Teoría de la semana 2 de Algorísmica Avanzada'")
s=s.replace('print(json.dumps(report,ensure_ascii=False,indent=2))',"print('Páginas',len(reader.pages),'previstas',len(pages)); [print(x['pagina'], x['primeras_lineas'][3:5], x['caracteres']) for x in mapping]")
(base/'tmp'/'pdfs'/'crear_guia_AA02.py').write_text(s,encoding='utf-8')
