"""Convert docs/11_Project_Guide.md to a Word document (python-docx, Windows).

    python tools\\md_to_docx.py <input.md> <output.docx>

Supports the Markdown used in the guide: #, ##, ### headings, paragraphs, **bold**, *italic*, `code`, bullets,
numbered lists, pipe tables, ``` code blocks, and callout quotes ("> **SAY THIS:** ..." etc.).
"""
import re
import sys

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

src, out = sys.argv[1], sys.argv[2]
lines = open(src, encoding='utf-8').read().split('\n')

NAVY = RGBColor(0x14, 0x2A, 0x4A)
BLUE = RGBColor(0x1F, 0x4F, 0xD8)
CALLOUT = {'SIMPLE VERSION': ('E4F3E8', '1E7A3C'), 'SAY THIS': ('E3EBFF', '1F4FD8'), 'CAREFUL': ('FFF1D0', 'B36B00')}

doc = Document()
sec = doc.sections[0]
sec.left_margin = sec.right_margin = Cm(2.2)
sec.top_margin = sec.bottom_margin = Cm(2.0)
st = doc.styles['Normal']
st.font.name, st.font.size = 'Calibri', Pt(11)
st.element.rPr.rFonts.set(qn('w:eastAsia'), 'Calibri')
st.paragraph_format.space_after = Pt(6)
for name, size, color in (('Heading 1', 20, NAVY), ('Heading 2', 15, BLUE), ('Heading 3', 12.5, NAVY)):
    h = doc.styles[name]
    h.font.name, h.font.size, h.font.bold, h.font.color.rgb = 'Calibri', Pt(size), True, color
    h.element.rPr.rFonts.set(qn('w:eastAsia'), 'Calibri')
    h.paragraph_format.space_before, h.paragraph_format.space_after = Pt(14), Pt(6)


def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill)
    tcPr.append(shd)


def borders(table, color='BFC7D1'):
    tblPr = table._tbl.tblPr
    b = OxmlElement('w:tblBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        e = OxmlElement('w:' + edge)
        e.set(qn('w:val'), 'single')
        e.set(qn('w:sz'), '4')
        e.set(qn('w:space'), '0')
        e.set(qn('w:color'), color)
        b.append(e)
    tblPr.append(b)


TOKEN = re.compile(r'(\*\*.+?\*\*|`.+?`|\*[^*\s][^*]*?\*)')


def runs(par, text, size=None, color=None, bold=False):
    for part in TOKEN.split(text):
        if not part:
            continue
        if part.startswith('**') and part.endswith('**'):
            r = par.add_run(part[2:-2])
            r.bold = True
        elif part.startswith('`') and part.endswith('`'):
            r = par.add_run(part[1:-1])
            r.font.name = 'Consolas'
            r.font.size = Pt((size or 11) - 1)
            r.font.color.rgb = RGBColor(0x8A, 0x1F, 0x4A)
            continue
        elif part.startswith('*') and part.endswith('*') and len(part) > 2:
            r = par.add_run(part[1:-1])
            r.italic = True
        else:
            r = par.add_run(part)
        if bold:
            r.bold = True
        if size:
            r.font.size = Pt(size)
        if color is not None:
            r.font.color.rgb = color


def callout(text):
    m = re.match(r'\*\*([A-Z ]+?)(?: \(.*?\))?:\*\*\s*(.*)', text)
    label = m.group(1) if m else ''
    fill, accent = CALLOUT.get(label, ('EEF1F5', '444444'))
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = t.rows[0].cells[0]
    shade(c, fill)
    borders(t, accent)
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(2)
    runs(p, text, 10.5)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def table(rows):
    rows = [r for r in rows if not re.match(r'^\|?\s*:?-{2,}', r.strip())]
    cells = [[c.strip() for c in r.strip().strip('|').split('|')] for r in rows]
    ncol = max(len(r) for r in cells)
    t = doc.add_table(rows=len(cells), cols=ncol)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    borders(t)
    for i, row in enumerate(cells):
        for j in range(ncol):
            cell = t.rows[i].cells[j]
            text = row[j] if j < len(row) else ''
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(1)
            if i == 0:
                shade(cell, '142A4A')
                runs(p, text, 9.5, RGBColor(255, 255, 255), bold=True)
            else:
                if i % 2 == 0:
                    shade(cell, 'F3F6FA')
                runs(p, text, 9.5)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


# footer with page numbers
fp = sec.footer.paragraphs[0]
fp.alignment = 1
r = fp.add_run('Autonomous Healthcare-Waste Collection Robot: Project Guide    |    page ')
r.font.size = Pt(8.5)
for kind, txt in (('begin', None), (None, 'PAGE'), ('end', None)):
    run = fp.add_run()
    run.font.size = Pt(8.5)
    if kind:
        f = OxmlElement('w:fldChar')
        f.set(qn('w:fldCharType'), kind)
        run._r.append(f)
    else:
        it = OxmlElement('w:instrText')
        it.set(qn('xml:space'), 'preserve')
        it.text = txt
        run._r.append(it)

i = 0
first_h1 = True
while i < len(lines):
    ln = lines[i]
    if ln.startswith('```'):
        i += 1
        block = []
        while i < len(lines) and not lines[i].startswith('```'):
            block.append(lines[i])
            i += 1
        t = doc.add_table(rows=1, cols=1)
        shade(t.rows[0].cells[0], 'F1F3F5')
        borders(t, 'C9CED6')
        p = t.rows[0].cells[0].paragraphs[0]
        r = p.add_run('\n'.join(block))
        r.font.name, r.font.size = 'Consolas', Pt(9)
        doc.add_paragraph().paragraph_format.space_after = Pt(2)
    elif ln.startswith('|'):
        block = []
        while i < len(lines) and lines[i].startswith('|'):
            block.append(lines[i])
            i += 1
        table(block)
        continue
    elif ln.startswith('# '):
        title = ln[2:]
        if title.startswith('Project Guide'):
            p = doc.add_paragraph()
            r = p.add_run('PROJECT GUIDE')
            r.bold, r.font.size, r.font.color.rgb = True, Pt(30), NAVY
            p2 = doc.add_paragraph()
            r2 = p2.add_run('Autonomous Healthcare-Waste Collection Robot')
            r2.bold, r2.font.size, r2.font.color.rgb = True, Pt(18), BLUE
        else:
            if not first_h1:
                doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
            doc.add_heading(title, 1)
        first_h1 = False
    elif ln.startswith('## '):
        doc.add_heading(ln[3:], 2)
    elif ln.startswith('### '):
        doc.add_heading(ln[4:], 3)
    elif ln.startswith('> '):
        callout(ln[2:])
    elif re.match(r'^\d+\.\s', ln):
        p = doc.add_paragraph(style='List Number')
        runs(p, re.sub(r'^\d+\.\s', '', ln))
    elif ln.startswith('- '):
        p = doc.add_paragraph(style='List Bullet')
        runs(p, ln[2:])
    elif ln.strip() == '---' or not ln.strip():
        pass
    else:
        p = doc.add_paragraph()
        runs(p, ln)
    i += 1

doc.save(out)
print('saved', out)
