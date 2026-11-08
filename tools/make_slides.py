"""Build the research-format presentation deck (python-pptx, Windows).

    python tools\\make_slides.py <slides_dir>
    powershell -File tools\\animate_slides.ps1 <slides_dir>\\HCW_Presentation.pptx      # optional animations
    powershell -File tools\\strip_animations.ps1 <in.pptx> <out.pptx>                    # optional: a no-animation copy

Structure (research format): cover, background (WHO statistics), problem statement, existing solutions and the gap,
proposed solution, methodology (system, environment, workflow), testing, demo, results, challenges, conclusion and
future work, thank you. Three themes alternate (CREAM, BLUE blueprint, INK). Each card is a group shape, so the whole
card animates as one. Shapes named "aNN_<effect>" are animated by animate_slides.ps1 (wipe, fade, fly, zoom, wipeP).
Speaker notes: Presenter 1 = slides 1-4, Presenter 2 = slides 5-9, Presenter 3 = slides 10-14.
"""
import os
import sys

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

D = sys.argv[1]
IMG = os.path.join(D, 'img')
VIDEO = os.path.join(os.path.dirname(D), 'video', 'hcw_demo_silent.mp4')
OUT = os.path.join(D, 'HCW_Presentation.pptx')


def rgb(h):
    return RGBColor(int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16))


THEMES = {
    'cream': dict(bg='#F6F1E6', head='#111418', body='#1F2328', muted='#555A62', card='#FFFFFF', line='#D8D0BF',
                  accent='#1F4FD8', chip='#111418', chip_t='#F6F1E6', pill='#111418', pill_t='#F6F1E6', hi='#E6ECFF'),
    'ink': dict(bg='#111418', head='#F6F1E6', body='#E9E5DC', muted='#B5B0A4', card='#1D2229', line='#3A424D',
                accent='#6C95FF', chip='#F6F1E6', chip_t='#111418', pill='#F6F1E6', pill_t='#111418', hi='#26304A'),
    'blue': dict(bg='#0B3F96', head='#FFFFFF', body='#E6EEFF', muted='#BCD0F5', card='#0F55C4', line='#7FA8F2',
                 accent='#FFFFFF', chip='#FFFFFF', chip_t='#0B3F96', pill='#FFFFFF', pill_t='#0B3F96', hi='#1B63D6'),
}
T = dict(THEMES['cream'])
HEAD, BODY = 'Impact', 'Segoe UI'

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]
order = {'n': 0}


def C(key):
    return rgb(T[key])


def anim(shape, kind):
    order['n'] += 1
    shape.name = 'a%02d_%s' % (order['n'], kind)
    return shape


def group(s, kind='fade'):
    """A group shape to put a whole card into; it animates as one object."""
    g = s.shapes.add_group_shape()
    anim(g, kind)
    return g


def rect(c, x, y, w, h, fill, shape=MSO_SHAPE.RECTANGLE, line=None, lw=1.0, rot=0):
    r = c.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is None:
        r.fill.background()
    else:
        r.fill.solid()
        r.fill.fore_color.rgb = fill
    if line is None:
        r.line.fill.background()
    else:
        r.line.color.rgb = line
        r.line.width = Pt(lw)
    r.shadow.inherit = False
    r.rotation = rot
    return r


def text(c, x, y, w, h, content, size=18, color=None, font=BODY, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, space=0, ls=1.0):
    color = color or C('body')
    tb = c.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.04)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    items = content if isinstance(content, list) else [content]
    for i, it in enumerate(items):
        t, o = (it, {}) if isinstance(it, str) else it
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = o.get('align', align)
        p.space_after = Pt(o.get('space', space))
        p.line_spacing = o.get('ls', ls)
        r = p.add_run()
        r.text = t
        r.font.name = o.get('font', font)
        r.font.size = Pt(o.get('size', size))
        r.font.bold = o.get('bold', bold)
        r.font.color.rgb = o.get('color', color)
    return tb


def notes(s, body):
    s.notes_slide.notes_text_frame.text = body


def asterisk(c, x, y, size=0.8, color=None):
    color = color or C('accent')
    for ang in (0, 60, 120):
        rect(c, x - size / 2, y - size * 0.09, size, size * 0.18, color, MSO_SHAPE.ROUNDED_RECTANGLE, rot=ang).adjustments[0] = 0.5


def new_slide(theme):
    global T
    T = dict(THEMES[theme])
    s = prs.slides.add_slide(BLANK)
    rect(s, 0, 0, 13.333, 7.5, C('bg'))
    if theme == 'blue':
        for i in range(1, 27):
            ln = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(i * 0.5), 0, Inches(i * 0.5), Inches(7.5))
            ln.line.color.rgb, ln.line.width = rgb('#2460C0'), Pt(0.5)
        for j in range(1, 15):
            ln = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, 0, Inches(j * 0.5), Inches(13.333), Inches(j * 0.5))
            ln.line.color.rgb, ln.line.width = rgb('#2460C0'), Pt(0.5)
    asterisk(s, 12.3, 0.85, 0.8)
    return s


def tag(s, label):
    text(s, 0.7, 0.32, 9, 0.4, label, 14, C('accent') if T['bg'] != '#0B3F96' else C('muted'), BODY, True)


def title(s, lines, size=64, x=0.65, y=0.7, w=11.0):
    tb = text(s, x, y, w, size / 72 * len(lines) + 0.4, [(l, {}) for l in lines], size, C('head'), HEAD, ls=0.9)
    return anim(tb, 'wipeP')


def card(c, x, y, w, h, hi=False, radius=0.07):
    r = rect(c, x, y, w, h, C('hi') if hi else C('card'), MSO_SHAPE.ROUNDED_RECTANGLE, line=C('line'), lw=1.25)
    r.adjustments[0] = radius
    return r


def chip(c, n, x, y, size=0.55):
    rect(c, x, y, size, size, C('chip'))
    text(c, x, y, size, size, str(n) + '.', 22, C('chip_t'), HEAD, False, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)


def pill(c, label, x, y, w, h, size=15):
    p = rect(c, x, y, w, h, C('pill'), MSO_SHAPE.ROUNDED_RECTANGLE)
    p.adjustments[0] = 0.5
    text(c, x, y, w, h, label, size, C('pill_t'), BODY, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    return p


def picture(c, name, x, y, w=None, h=None):
    kw = {}
    if w:
        kw['width'] = Inches(w)
    if h:
        kw['height'] = Inches(h)
    p = c.shapes.add_picture(os.path.join(IMG, name), Inches(x), Inches(y), **kw)
    p.line.color.rgb, p.line.width = C('head'), Pt(2.5)
    return p


# ============================================================ 1 cover (cream)
s = new_slide('cream')
text(s, 0.7, 0.32, 8, 0.4, 'IEEE RWANDA MENTORSHIP PROGRAM', 14, C('accent'), BODY, True)
anim(text(s, 0.7, 0.9, 6, 0.8, 'AUTONOMOUS', 40, C('accent'), HEAD), 'wipe')
anim(text(s, 0.65, 1.45, 7.9, 3.8, [('HEALTHCARE', {'size': 92}), ('WASTE', {'size': 92}), ('COLLECTION ROBOT', {'size': 54})], 90, C('head'), HEAD, ls=0.88), 'wipeP')
anim(text(s, 0.7, 5.3, 7.9, 0.4, 'From a real problem to a tested simulated solution.', 16, C('body')), 'fade')
anim(text(s, 0.7, 5.95, 3, 0.4, 'PRESENTED BY:', 18, C('head'), HEAD), 'fade')
anim(text(s, 0.7, 6.3, 8.2, 0.4, 'Damilare Lekan Adekeye   |   David Parsley Kakhayanga   |   Beni Bonheur Karangwa', 15, C('body')), 'fade')
anim(text(s, 0.7, 6.7, 6, 0.4, 'MENTOR: Miracle James', 15, C('accent'), BODY, True), 'fade')
g = group(s, 'fly')
rect(g, 8.95, 1.85, 3.9, 2.55, C('accent'))
picture(g, 'bay.png', 8.6, 1.5, w=3.9)
notes(s, "PRESENTER 1 (slides 1 to 4)\n\n"
         "Good day everyone. We are Damilare, David and Beni, and our mentor is Miracle James. "
         "Our project is an autonomous healthcare-waste collection robot. We will follow the path of a research project: the background and the problem we saw, "
         "what already exists, our proposed solution, how we built and tested it, what we found, and where it can go next.\n\n"
         "Say clearly that the demonstration is a simulation of the robot in a clinic.")

# ============================================================ 2 background (ink)
s = new_slide('ink')
tag(s, '01  /  BACKGROUND')
title(s, ['THE SCALE OF THE', 'PROBLEM'], 60)
stats = [('85%  /  15%', 'of health-care waste is general / hazardous. The hazardous part may be infectious, toxic or radioactive.'),
         ('16 BILLION', 'injections are given worldwide every year. Not all needles and syringes are disposed of safely.'),
         ('30%', 'chance of hepatitis B infection after one needle-stick from an infected source (hepatitis C: 1.8%, HIV: 0.3%).'),
         ('24%', 'of health facilities in sub-Saharan Africa had basic waste management in 2025. Worldwide: 71%.')]
for i, (big, small) in enumerate(stats):
    x = 0.65 + i * 3.1
    g = group(s, 'fade')
    card(g, x, 2.65, 2.9, 3.55)
    text(g, x + 0.15, 2.85, 2.6, 1.0, big, 38 if len(big) < 12 else 30, C('accent'), HEAD, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(g, x + 0.2, 4.0, 2.5, 2.1, small, 15, C('body'), align=PP_ALIGN.CENTER)
text(s, 0.65, 6.4, 12.1, 0.8, 'Sources: WHO fact sheet "Health-care waste"; WHO injection safety fact sheet; WHO/UNICEF Joint Monitoring Programme report on health care facilities 2015-2025 (published 18 August 2026).', 12, C('muted'))
notes(s, "We begin with the background, using figures from the World Health Organization.\n\n"
         "WHO says about 85 percent of the waste produced by health-care activities is general waste, and about 15 percent is hazardous: it may be infectious, toxic or radioactive.\n"
         "About 16 billion injections are given worldwide every year, and not all needles and syringes are disposed of safely. WHO gives the risk of infection after a single needle-stick from an infected source as about 30 percent for hepatitis B, 1.8 percent for hepatitis C and 0.3 percent for HIV.\n"
         "And in the 2026 WHO and UNICEF report on health facilities, only 24 percent of facilities in sub-Saharan Africa had basic waste management in 2025, compared with 71 percent worldwide.\n\n"
         "Be ready to say where the numbers come from: the WHO health-care waste fact sheet, the WHO injection safety fact sheet, and the WHO/UNICEF 2026 report. "
         "The per-needle-stick risks are for one exposure to an infected source, not the chance for every health worker.")

# ============================================================ 3 problem statement (cream)
s = new_slide('cream')
tag(s, '02  /  PROBLEM STATEMENT')
title(s, ['PROBLEM STATEMENT'], 64)
g = group(s, 'fade')
card(g, 0.65, 1.85, 12.05, 1.95, hi=True)
text(g, 0.95, 1.95, 11.5, 1.8, 'Hazardous healthcare waste is still carried by hand from the rooms where it is produced to the storage area. This exposes staff to risk, depends on people not mixing up containers, leaves little record of what moved, and uses repetitive staff time. Many existing robots are expensive or built for large facilities.', 20, C('head'), BODY, True, anchor=MSO_ANCHOR.MIDDLE)
text(s, 0.65, 4.0, 8, 0.4, 'WHAT WE IDENTIFIED BEFORE BUILDING ANYTHING', 16, C('accent'), HEAD)
probs = [('RISKY HANDLING', 'Infectious and sharp waste can harm anyone who carries it.'),
         ('MIX-UPS', 'Taking or mixing up the wrong container is a safety incident.'),
         ('WEAK RECORDS', 'Manual notes depend on people remembering to write.'),
         ('REPETITIVE WORK', 'The same walk many times a day, which tires people.')]
for i, (h, b) in enumerate(probs):
    x = 0.65 + i * 3.1
    g = group(s, 'fade')
    card(g, x, 4.5, 2.9, 2.4)
    chip(g, i + 1, x + 0.2, 4.7, 0.5)
    text(g, x + 0.2, 5.35, 2.55, 0.5, h, 22, C('head'), HEAD)
    text(g, x + 0.2, 5.85, 2.55, 1.0, b, 14, C('body'))
notes(s, "This is our problem statement, the problem we identified before we built anything.\n\n"
         "Hazardous healthcare waste is still carried by hand from the rooms where it is produced to the storage area. That creates four problems. "
         "Risky handling: infectious and sharp waste can harm whoever carries it. Mix-ups: taking or confusing the wrong container is a safety incident. "
         "Weak records: manual notes depend on people remembering. And repetitive work: the same walk many times a day.\n\n"
         "Our proposal also noted that many existing robots are expensive, complex, or designed for large commercial facilities, so there is room for a smaller, more affordable prototype.")

# ============================================================ 4 existing solutions and the gap (blue)
s = new_slide('blue')
tag(s, '03  /  EXISTING SOLUTIONS AND THE GAP')
title(s, ['WHAT ALREADY EXISTS'], 60)
robots = [('MOXI', 'Diligent Robotics', 'Delivers medicines, lab samples and PPE. Can use elevators and secure doors where supported.'),
          ('TUG / T3', 'Aethon', 'Moves supplies, meals, linen and trash or regulated waste on carts. Our closest baseline.'),
          ('RELAY', 'Relay Robotics', 'Point-to-point delivery of specimens, medicines and supplies inside hospitals.'),
          ('RWANDA', 'COVID-19 and UV-C robots', 'Screening, monitoring and disinfection robots in Rwandan hospitals. They do not carry waste.')]
for i, (h, sub, b) in enumerate(robots):
    x = 0.65 + i * 3.1
    g = group(s, 'fade')
    card(g, x, 1.95, 2.9, 2.75)
    text(g, x + 0.2, 2.05, 2.55, 0.5, h, 26, C('head'), HEAD)
    text(g, x + 0.2, 2.6, 2.55, 0.4, sub, 13, C('muted'), BODY, True)
    text(g, x + 0.2, 3.05, 2.55, 1.6, b, 14, C('body'))
g = group(s, 'fade')
bar = rect(g, 0.65, 4.95, 12.05, 1.95, C('pill'), MSO_SHAPE.ROUNDED_RECTANGLE)
bar.adjustments[0] = 0.08
text(g, 0.95, 5.0, 2.6, 0.5, 'THE GAP', 30, C('pill_t'), HEAD)
text(g, 0.95, 5.55, 11.4, 1.3, 'Autonomous hospital logistics, even waste transport, already exists. Our focus is the combination of waste-container collection, camera verification of the right container, indoor navigation and task management, built as an affordable, open-source, simulation-first prototype.', 17, C('pill_t'), BODY, True)
notes(s, "Next, what already exists. This comes from our own research on existing hospital robots.\n\n"
         "Moxi, from Diligent Robotics, delivers medicines, lab samples and PPE, and can use elevators and secure doors where supported. "
         "TUG and T3, from Aethon, move supplies, meals, linen and also trash and regulated waste. That makes TUG our closest baseline. "
         "Relay does point-to-point delivery of specimens, medicines and supplies. And in Rwanda, robots have been used during COVID-19 for screening and monitoring, and UV-C disinfection robots at Nyarugenge District Hospital, but those do not carry waste.\n\n"
         "So autonomous hospital logistics, even waste transport, exists. We are not claiming to be first. Our focus is the combination of collecting waste containers, using the camera to verify the right container, indoor navigation, and task management, as an affordable open-source, simulation-first prototype.\n\n"
         "Now my colleague will present our proposed solution and methodology.")

# ============================================================ 5 proposed solution (cream)
s = new_slide('cream')
tag(s, '04  /  PROPOSED SOLUTION')
title(s, ['OUR PROPOSED SOLUTION'], 60)
g = group(s, 'fade')
card(g, 0.65, 1.85, 12.05, 1.35, hi=True)
text(g, 0.95, 1.9, 1.5, 0.4, 'AIM', 16, C('accent'), HEAD)
text(g, 0.95, 2.25, 11.5, 0.95, 'To design and demonstrate, in simulation, an autonomous robot that collects sealed healthcare-waste containers on request, verifies them, and delivers them to a hazardous-waste store.', 17, C('head'), BODY, True)
objs = ['Navigate autonomously on a map of a clinic.', 'Identify and verify the right container with a camera tag.',
        'Carry it (simulated magnet) and deliver it to storage.', 'Refuse and report when the container is wrong or missing.',
        'Test it repeatedly and record the results.']
g = group(s, 'fade')
card(g, 0.65, 3.4, 7.2, 3.5)
text(g, 0.95, 3.5, 6, 0.4, 'OBJECTIVES', 16, C('accent'), HEAD)
for i, o in enumerate(objs):
    y = 3.95 + i * 0.58
    chip(g, i + 1, 0.95, y, 0.46)
    text(g, 1.55, y, 6.1, 0.5, o, 15, C('body'), anchor=MSO_ANCHOR.MIDDLE)
g = group(s, 'fade')
card(g, 8.1, 3.4, 4.6, 3.5)
text(g, 8.4, 3.5, 4, 0.4, 'SCOPE', 16, C('accent'), HEAD)
text(g, 8.4, 3.95, 4.05, 2.9, [('Sealed, already-sorted containers only.', {'space': 8}),
                              ('The robot does not sort, open or process waste.', {'space': 8}),
                              ('Simulation first, real robot next.', {})], 16, C('body'), BODY, True)
notes(s, "PRESENTER 2 (slides 5 to 9)\n\n"
         "Our proposed solution. The aim: to design and demonstrate, in simulation, an autonomous robot that collects sealed healthcare-waste containers on request, verifies them, and delivers them to a hazardous-waste store.\n\n"
         "Five objectives: navigate on a map of a clinic; identify and verify the right container with a camera tag; carry it with a simulated magnet and deliver it to storage; refuse and report when the container is wrong or missing; and test it repeatedly and record the results.\n\n"
         "The scope is deliberate. The robot moves sealed, already-sorted containers. It does not sort, open or process waste. Sorting is done by the staff who fill the bin. "
         "And we work simulation first, with a real robot as the next step.")

# ============================================================ 6 methodology: system design (blue)
s = new_slide('blue')
tag(s, '05  /  METHODOLOGY  1  OF  3')
title(s, ['SYSTEM DESIGN'], 60)
g = group(s, 'fade')
pill(g, 'REQUEST: ROOM A, B OR C', 4.5, 1.95, 4.3, 0.65, 17)
blocks = [('TASK MANAGER', 'The brain. Runs the 7 steps in order, decides when to stop, and logs every task.'),
          ('NAVIGATION', 'Nav2 plans and drives. A map from SLAM and AMCL tell the robot where it is.'),
          ('PERCEPTION', 'Camera + AprilTag. The expected tag must be seen in 5 frames in a row, and no other tag.'),
          ('SIMULATED MAGNET', 'Attaches the container to the robot and releases it at the storage bay.')]
for i, (h, b) in enumerate(blocks):
    x = 0.65 + i * 3.1
    g = group(s, 'fade')
    card(g, x, 2.95, 2.9, 2.85, radius=0.06)
    chip(g, i + 1, x + 0.22, 3.15, 0.5)
    text(g, x + 0.2, 3.8, 2.55, 0.5, h, 22, C('head'), HEAD)
    text(g, x + 0.2, 4.35, 2.55, 1.4, b, 14, C('body'))
g = group(s, 'fade')
pill(g, 'ROS 2 JAZZY   |   TURTLEBOT 4 IN A GAZEBO CLINIC   |   CAMERA + LIDAR', 0.65, 6.15, 12.05, 0.7, 17)
notes(s, "The methodology has three parts: the system design, the environment, and the task workflow.\n\n"
         "System design. There are four building blocks. The task manager is the brain: it runs the seven steps in order, decides when to stop, and logs every task. "
         "Navigation uses Nav2, with a map built by SLAM and AMCL to find the robot's position. "
         "Perception uses the camera and AprilTag markers: a container is verified only when the expected tag is seen in five frames in a row and no other tag is seen. "
         "The magnet is simulated.\n\n"
         "A design rule from our mentor: only Nav2 moves the robot, so the task manager and the perception code never send wheel commands. "
         "Everything runs on ROS 2 Jazzy, with a TurtleBot 4 in a Gazebo clinic.")

# ============================================================ 7 methodology: environment and map (cream)
s = new_slide('cream')
tag(s, '05  /  METHODOLOGY  2  OF  3')
title(s, ['ENVIRONMENT AND MAP'], 60)
g = group(s, 'fly')
picture(g, 'map.png', 0.65, 1.95, h=4.2)
g = group(s, 'fly')
picture(g, 'bay.png', 5.55, 1.95, w=4.3)
text(s, 0.65, 6.25, 4.6, 0.7, 'Map of the clinic ground floor with the named places: Home, A, B, C and Storage.', 12, C('muted'))
text(s, 5.55, 4.9, 4.3, 0.4, 'The hazardous-waste storage bay', 13, C('muted'))
pts = [('SIMULATED CLINIC', 'Open-RMF clinic, ground floor, in Gazebo, with a TurtleBot 4.'),
       ('MAP', 'Built once with SLAM, then used by AMCL and Nav2.'),
       ('PLACES AND TAGS', 'Rooms A, B, C and storage in one settings file. Tags 11, 12, 13 on the containers.')]
for i, (h, b) in enumerate(pts):
    y = 1.95 + i * 1.6
    g = group(s, 'fade')
    card(g, 10.05, y, 2.75, 1.5)
    text(g, 10.15, y + 0.06, 2.55, 0.4, h, 16, C('head'), HEAD)
    text(g, 10.15, y + 0.45, 2.55, 1.0, b, 12, C('body'))
notes(s, "The environment. We used the ground floor of the Open-RMF clinic, a well-known open-source hospital world, in the Gazebo simulator, with a TurtleBot 4 robot.\n\n"
         "The map on the left was built once by the robot with SLAM. Nav2 and AMCL then use it to navigate and to find the robot's position. We marked the named places on it: Home, the three collection rooms A, B and C, and Storage. "
         "Those places and the container tags are kept in one settings file, so a new place is a small edit.\n\n"
         "Each collection room has a container with its own tag: 11 for A, 12 for B, 13 for C. The storage area is dressed as a hazardous-waste store, with a hazard-striped floor, shelves, signs and bins, which is the picture in the middle.")

# ============================================================ 8 methodology: task workflow (ink)
s = new_slide('ink')
tag(s, '05  /  METHODOLOGY  3  OF  3')
title(s, ['TASK WORKFLOW'], 60)
steps = ['Drive to the collection room', 'Verify the container tag', 'Attach with the magnet', 'Carry to the storage bay',
         'Release at storage', 'Report completion', 'Drive back home']
for i, t in enumerate(steps):
    y = 1.95 + i * 0.7
    g = group(s, 'fade')
    card(g, 0.65, y, 5.6, 0.58, hi=(i == 1), radius=0.25)
    chip(g, i + 1, 0.65, y, 0.58)
    text(g, 1.4, y, 4.8, 0.58, t, 17, C('head'), BODY, i == 1, anchor=MSO_ANCHOR.MIDDLE)
picture(s, 'panel_done.png', 6.75, 1.9, w=3.0)
picture(s, 'panel_refusal.png', 9.95, 1.9, w=3.0)
text(s, 6.75, 5.25, 3.0, 0.6, 'A normal task: every step ticked, green result', 13, C('muted'), align=PP_ALIGN.CENTER)
text(s, 9.95, 5.25, 3.0, 0.6, 'A wrong container: red stop at the check', 13, C('muted'), align=PP_ALIGN.CENTER)
pill(s, 'STEP 2 IS THE SAFETY GATE', 6.75, 5.9, 6.2, 0.55, 16)
text(s, 6.75, 6.5, 6.2, 0.6, 'Wrong tag, no tag or an unstable tag: no pick-up. The robot goes home and logs the cause.', 14, C('body'))
notes(s, "The task workflow. One task has seven steps: drive to the collection room, verify the container tag, attach with the magnet, carry to the storage bay, release, report, and drive home.\n\n"
         "The two pictures on the right are the status panel you will see in the video. On the left, a normal task: all steps ticked and a green result. "
         "On the right, a failure: the camera saw tag 13 but tag 12 was expected, so the robot stopped at the check, picked nothing up, and went home.\n\n"
         "Step two is the safety gate for the whole project. If the tag is wrong, missing or unstable, the robot does not pick up.")

# ============================================================ 9 testing methodology (cream)
s = new_slide('cream')
tag(s, '06  /  TESTING METHODOLOGY')
title(s, ['HOW WE TESTED IT'], 60)
tests = [('UNIT TESTS', '8 automated tests of the verification rule, including wrong-tag and unstable-tag cases.'),
         ('INTEGRATION', 'Drive home, A, B, C, storage, home with tag checks: 15 of 15 legs, correct tag 9 of 9.'),
         ('END-TO-END TASKS', 'Complete tasks to A, B and C, repeated in unattended batches.'),
         ('FAULT INJECTION', 'Wrong container, missing container, blocked corridor, busy and invalid requests.'),
         ('REGRESSION', 'Re-run after every code or setting change (including 7 and 8 November).'),
         ('ROOT-CAUSE ANALYSIS', 'Camera frames saved at failures and the robot position logged every 0.5 s.')]
for i, (h, b) in enumerate(tests):
    x = 0.65 + (i % 3) * 4.1
    y = 1.9 + (i // 3) * 2.2
    g = group(s, 'fade')
    card(g, x, y, 3.9, 2.0)
    chip(g, i + 1, x + 0.2, y + 0.18, 0.46)
    text(g, x + 0.8, y + 0.2, 2.95, 0.45, h, 20, C('head'), HEAD, anchor=MSO_ANCHOR.MIDDLE)
    text(g, x + 0.25, y + 0.8, 3.45, 1.15, b, 14, C('body'))
g = group(s, 'fade')
pill(g, 'RECORDED FOR EVERY TASK: RESULT, TIME PER STAGE, CAUSE OF ANY FAILURE', 0.65, 6.4, 12.05, 0.55, 15)
notes(s, "How we tested. We used six kinds of testing.\n\n"
         "Unit tests: eight automated tests of the verification rule, including wrong-tag and unstable-tag cases, because the rule decides when it is safe to pick up.\n"
         "Integration tests: we drove home, A, B, C, storage and home with tag checks. 15 of 15 legs completed and the correct tag was detected 9 of 9 times.\n"
         "End-to-end tasks: complete tasks to A, B and C, repeated in unattended batches.\n"
         "Fault injection: we deliberately caused a wrong container, a missing container, a blocked corridor, a request while busy, and an invalid request, because a safety system is judged by how it fails.\n"
         "Regression tests: we re-ran the tests after every change.\n"
         "Root-cause analysis: when something failed, we saved camera frames and logged the robot's position to find the real cause.\n\n"
         "For every task we record the result, the time per stage, and the cause of any failure.\n\n"
         "Note: nothing here was machine-learned. The 67 tasks are test runs, not training data.")

# ============================================================ 10 demo (ink)
s = new_slide('ink')
tag(s, '07  /  DEMONSTRATION')
title(s, ['SEE IT RUN'], 54, y=0.7, w=8)
s.shapes.add_movie(VIDEO, Inches(2.2), Inches(1.7), Inches(8.9), Inches(5.0), poster_frame_image=os.path.join(IMG, 'verify_A.png'), mime_type='video/mp4')
text(s, 1.6, 6.8, 10.1, 0.4, 'A normal task at room A, then a wrong container at room B. Silent video, 2 min 40 s.', 13, C('muted'), align=PP_ALIGN.CENTER)
notes(s, "PRESENTER 3 (slides 10 to 14)\n\n"
         "We will now play the demonstration video. It has no sound, so we will explain while it plays.\n\n"
         "First, a normal task at room A: the robot is called, drives there, checks the tag, picks the container up, and carries it to the hazardous-waste bay. "
         "Parts are sped up and the speed is shown in the corner.\n\n"
         "Then a failure: a wrong container is at room B. Watch the panel on the right. The camera sees tag 13, but tag 12 is expected, and the robot refuses and goes home.\n\n"
         "If the video does not play, say so and move on; the screenshots on slide 8 show the same two cases. Click the video once to start it.")

# ============================================================ 11 results (cream)
s = new_slide('cream')
tag(s, '08  /  RESULTS IN SIMULATION')
title(s, ['THE NUMBERS'], 54, y=0.7, w=9)
for i, (big, small, col) in enumerate([('67/67', 'NORMAL TASKS COMPLETED', C('head')), ('6/6', 'STAGED FAULTS REFUSED WITH THE CORRECT CAUSE', C('accent'))]):
    x = 0.65 + i * 6.2
    g = group(s, 'zoom')
    card(g, x, 1.85, 5.95, 2.95)
    text(g, x, 1.95, 5.95, 1.9, big, 130, col, HEAD, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(g, x + 0.2, 3.95, 5.55, 0.7, small, 17, C('head'), BODY, True, PP_ALIGN.CENTER)
g = group(s, 'fade')
card(g, 0.65, 5.05, 5.95, 1.95)
text(g, 0.95, 5.12, 5.4, 0.4, 'NORMAL TASKS BY ROOM', 20, C('head'), HEAD)
for i, (r, n, col) in enumerate([('Room A', 37, '#2E6BFF'), ('Room B', 15, '#1FA85A'), ('Room C', 15, '#F08A00')]):
    y = 5.6 + i * 0.45
    text(g, 0.95, y, 1.2, 0.4, r, 14, C('body'))
    rect(g, 2.1, y + 0.07, 3.3 * n / 37, 0.26, rgb(col), MSO_SHAPE.ROUNDED_RECTANGLE)
    text(g, 2.15 + 3.3 * n / 37, y, 0.8, 0.4, str(n), 14, C('head'), BODY, True)
g = group(s, 'fade')
card(g, 6.85, 5.05, 5.95, 1.95)
text(g, 7.15, 5.12, 5.4, 0.4, 'WHAT IT SHOWS', 20, C('head'), HEAD)
text(g, 7.15, 5.6, 5.4, 1.35, 'The full chain works end to end, about 89 s from request to report on average. All the wrong or missing containers we staged were caught and refused.', 15, C('body'))
notes(s, "Our results, from the simulation. We logged 67 normal tasks and all 67 completed: 37 to room A, 15 to room B and 15 to room C. A task took about 89 seconds from request to completion report on average.\n\n"
         "We also staged 6 faults, such as a wrong container or a missing container, and the robot refused all 6, with the correct cause written in the log.\n\n"
         "These are simulation results. They show the whole chain works from request to report, and that the safety check does its job. "
         "With 67 successful runs we can say, with 95 percent confidence, that the true success rate is at least about 96 percent. The next step is more runs and then real hardware.")

# ============================================================ 12 challenges (blue)
s = new_slide('blue')
tag(s, '09  /  CHALLENGES AND IMPROVEMENTS')
title(s, ['WHAT WE FIXED'], 54, y=0.7, w=10)
probs = [('SLOW TRIPS TO ROOM A', 'Some trips took 84 to 98 seconds. Logging the robot position showed it stopped 0.02 rad outside its turning tolerance and kept correcting.', 'We widened the heading tolerance from 0.10 to 0.15 rad. Trips to A then took about 39 seconds.'),
         ('SIMULATION TOO SLOW', 'With hundreds of models, the simulator ran at only 1 to 3 percent of real time.', 'We simplified the world and kept decoration to simple shapes. It now runs near real time.'),
         ('CONTAINER LEFT IN THE CORRIDOR', 'The first version released the container in the middle of a hallway. It looked wrong and unsafe.', 'We moved the drop point against the wall and built a marked hazardous-waste bay there.')]
for i, (h, p, f) in enumerate(probs):
    y = 1.85 + i * 1.7
    g = group(s, 'fade')
    card(g, 0.65, y, 12.05, 1.55)
    chip(g, i + 1, 0.85, y + 0.5, 0.55)
    text(g, 1.65, y + 0.15, 2.7, 1.3, h, 22, C('head'), HEAD, anchor=MSO_ANCHOR.MIDDLE, ls=0.95)
    text(g, 4.55, y + 0.1, 4.0, 0.3, 'PROBLEM', 12, C('muted'), BODY, True)
    text(g, 4.55, y + 0.4, 4.05, 1.15, p, 13, C('body'))
    text(g, 8.8, y + 0.1, 3.8, 0.3, 'FIX', 12, C('muted'), BODY, True)
    text(g, 8.8, y + 0.4, 3.8, 1.15, f, 13, C('head'), BODY, True)
notes(s, "Not everything worked at first. Three examples.\n\n"
         "One: trips to room A were sometimes very slow, 84 to 98 seconds. We recorded the robot's position when it stalled and found it was a tiny fraction of a radian outside its turning tolerance, so it kept correcting. "
         "We widened that tolerance a little, and trips to A went back to about 39 seconds.\n\n"
         "Two: the simulation ran at only one to three percent of real time because the world had too many objects. We simplified it.\n\n"
         "Three: the first version dropped the container in the middle of the hallway. We moved the drop point to the wall and built a proper marked storage bay.")

# ============================================================ 13 conclusion and future work (cream)
s = new_slide('cream')
tag(s, '10  /  CONCLUSION AND FUTURE WORK')
title(s, ['CONCLUSION', 'AND FUTURE WORK'], 54, y=0.7, w=10)
g = group(s, 'fade')
card(g, 0.65, 2.75, 6.0, 4.15, hi=True)
text(g, 0.95, 2.85, 5.4, 0.4, 'WHAT WE ACHIEVED', 20, C('head'), HEAD)
text(g, 0.95, 3.45, 5.45, 3.4, [('A working simulated robot: request, drive, verify, carry, deliver, report, return home.', {'space': 16}),
                               ('A safety check that refuses wrong or missing containers: 6 of 6 staged faults.', {'space': 16}),
                               ('67 of 67 normal tasks completed in simulation.', {})], 19, C('body'), BODY, True)
g = group(s, 'fade')
card(g, 6.9, 2.75, 5.8, 4.15)
text(g, 7.2, 2.85, 5.2, 0.4, 'FUTURE WORK', 20, C('head'), HEAD)
text(g, 7.2, 3.45, 5.25, 3.4, [('A real TurtleBot 4 with a real magnet or gripper.', {'space': 14}),
                              ('Many more tests, including failures while carrying.', {'space': 14}),
                              ('A request screen and alerts when a task is refused.', {'space': 14}),
                              ('More rooms and floors, and several robots working together.', {})], 19, C('body'), BODY)
notes(s, "To conclude. We set out to build, in simulation, a robot that collects sealed healthcare-waste containers, checks them, and delivers them to a hazardous-waste store. "
         "We achieved a working simulated robot that goes through every step, a safety check that refused all 6 staged faults, and 67 of 67 normal tasks completed.\n\n"
         "For future work: a real TurtleBot 4 with a real magnet or gripper, many more tests including failures while carrying, a request screen with alerts when a task is refused, "
         "and more rooms and floors, even several robots working together. These are ideas for how we can improve it further.")

# ============================================================ 14 thanks (ink)
s = new_slide('ink')
tag(s, 'IEEE RWANDA MENTORSHIP PROGRAM')
anim(text(s, 0.65, 1.2, 11.5, 2.2, 'THANK YOU', 130, C('head'), HEAD, ls=0.9), 'wipe')
anim(text(s, 0.7, 3.5, 8, 0.8, 'QUESTIONS?', 54, C('accent'), HEAD), 'fade')
anim(text(s, 0.7, 4.8, 9, 0.4, 'PRESENTED BY:', 18, C('head'), HEAD), 'fade')
anim(text(s, 0.7, 5.2, 11, 0.4, 'Damilare Lekan Adekeye   |   David Parsley Kakhayanga   |   Beni Bonheur Karangwa', 15, C('body')), 'fade')
anim(text(s, 0.7, 5.6, 8, 0.4, 'MENTOR: Miracle James', 15, C('muted'), BODY, True), 'fade')
anim(text(s, 0.7, 6.4, 11, 0.4, 'github.com/damilareadekeye/AUTONOMOUS-HEALTHCARE-WASTE-COLLECTION-ROBOT', 14, C('accent')), 'fade')
notes(s, "Thank you for listening. We are happy to take your questions.\n\n"
         "Likely questions and short honest answers (for us only; the full list is in docs/11_Project_Guide.md):\n"
         "- Is it a real robot? Not yet. We built and tested it in simulation, and the same software is designed to move to a real TurtleBot 4.\n"
         "- What if a nurse puts the wrong waste in the wrong bin? That is a sorting problem upstream. Our robot transports sealed, already-sorted containers and makes sure the right one goes to the right place.\n"
         "- Where is the storage? It is a marked hazardous-waste bay in the corridor. A separate room would need a new section of the map and new tuning.\n"
         "- Did you train a model? No. The robot uses planning, a map and tag detection. The 67 tasks are test runs, not training data.\n"
         "- What if the robot moves to another place in the hospital? We update the map for that area (remapping) and the list of places, then re-test.")

# ---------------------------------------------------------------- safety check: nothing outside the slide
W, H = prs.slide_width, prs.slide_height
bad = []
for n, sl in enumerate(prs.slides, 1):
    for sh in sl.shapes:
        if sh.rotation:
            continue
        if sh.left < -10 or sh.top < -10 or sh.left + sh.width > W + 10 or sh.top + sh.height > H + 10:
            bad.append((n, sh.name, round(sh.left / 914400, 2), round(sh.top / 914400, 2), round(sh.width / 914400, 2), round(sh.height / 914400, 2)))
print('shapes outside the slide:', bad if bad else 'none')
prs.save(OUT)
print('saved', OUT, 'slides:', len(prs.slides))
